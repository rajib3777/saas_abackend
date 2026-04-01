import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
import requests
from bs4 import BeautifulSoup
from .models import Parcel

logger = logging.getLogger(__name__)

def scrape_steadfast_status(tracking_number):
    """
    Scrapes the Steadfast Courier tracking site.
    Since we don't have the exact DOM structure, we use a heuristic based on tracking timeline text.
    """
    try:
        url = f"https://steadfast.com.bd/t/{tracking_number}"
        # Provide user-agent to avoid basic blocks
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # The tracking timeline or status block usually resides in specific containers.
        # We will extract all text from the body and look for the definitive last status.
        # Or look for badge classes that indicate status.
        body_text = soup.body.get_text(separator=' ', strip=True).lower() if soup.body else ""
        
        # It's better to look for exact phrase patterns Steadfast uses.
        # Example: 'status: delivered', 'order delivered', etc.
        # We will use a fallback prioritized search:
        
        if 'delivered' in body_text and not ('out for delivery' in body_text and body_text.index('out for delivery') > body_text.rfind('delivered')):
            # Ensuring delivered is the latest major state
             return 'delivered', "Successfully Delivered"
        if 'returned' in body_text or 'return in progress' in body_text:
            return 'returned', "Returned to sender"
        if 'out for delivery' in body_text or 'delivery man' in body_text:
             return 'out_for_delivery', "Out for Delivery"
        if 'in transit' in body_text or 'dispatched' in body_text or 'received at' in body_text or 'transit' in body_text:
             return 'in_transit', "In Transit"
             
        # Not found any specific update, so it might be pending or the tracking ID is not found.
        if 'not found' in body_text:
            return 'pending', "Tracking ID not found yet"
            
        return 'pending', "Pending / No updates yet"
            
    except Exception as e:
        logger.error(f"Error scraping Steadfast tracking {tracking_number}: {e}")
        return None, str(e)


@shared_task
def track_due_parcels():
    now = timezone.now()
    due_parcels = Parcel.objects.filter(
        is_auto_tracking=True, 
        next_check__lte=now
    ).exclude(status__in=['delivered', 'returned', 'cancelled'])
    
    processed = 0
    for parcel in due_parcels:
        new_status, note = scrape_steadfast_status(parcel.tracking_number)
        
        interval = 30 # Default if something fails
        
        if new_status:
            # Map intervals based on status
            if new_status == 'pending':
                interval = 10
            elif new_status == 'in_transit':
                interval = 30
            elif new_status == 'out_for_delivery':
                interval = 15
            elif new_status in ['delivered', 'returned', 'cancelled']:
                interval = 0 # stop tracking
                
            if interval > 0:
                parcel.next_check = now + timedelta(minutes=interval)
            else:
                parcel.next_check = None 
                parcel.is_auto_tracking = False 
                
            if parcel.status != new_status:
                parcel.status = new_status
                
            parcel.last_sync_status = f"Synced: {note}"
        else:
            # Scrape failed (e.g., timeout, 500, blocked), retry in 10 mins
            interval = 10 
            parcel.next_check = now + timedelta(minutes=interval)
            parcel.last_sync_status = f"Failed to sync. Retry in 10m"
            
        parcel.last_sync_time = now
        parcel.save(update_fields=['status', 'next_check', 'is_auto_tracking', 'last_sync_time', 'last_sync_status'])
        processed += 1
        
    return f"Processed {processed} tracking updates."
