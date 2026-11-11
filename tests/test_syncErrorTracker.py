import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app.syncErrorTracker import SyncErrorTracker

list_name = 'mockedList'
list_item = 'mockedItem'
exception = Exception('mockedException')

def test_initial_health_state():
    tracker = SyncErrorTracker()
    assert tracker.healthy == True
    
def test_unhealthy_after_same_errors():
    tracker = SyncErrorTracker(unhealthy_after=2)
    tracker.record_error(list_name, list_item, exception)
    assert tracker.healthy == True
    
    tracker.record_error(list_name, list_item, exception)
    assert tracker.healthy == False
    
def test_healthy_after_different_errors():
    tracker = SyncErrorTracker(unhealthy_after=2)
    tracker.record_error(list_name, list_item, exception)
    assert tracker.healthy == True
    
    tracker.record_error(list_name, 'anotherItem', exception)
    assert tracker.healthy == True
    
def test_healthy_after_errors_resolved():
    tracker = SyncErrorTracker(unhealthy_after=2)
    tracker.record_error(list_name, list_item, exception)
    assert tracker.healthy == True
    
    tracker.record_error(list_name, list_item, exception)
    assert tracker.healthy == False
    
    tracker.successful_sync(list_name, list_item)
    assert tracker.healthy == True

def test_no_collision_between_similar_names():
    tracker = SyncErrorTracker(unhealthy_after=2)
    tracker.record_error('a_b', 'c', exception)
    tracker.record_error('a', 'b_c', exception)
    assert tracker.healthy == True

    tracker.successful_sync('a_b', 'c')
    tracker.record_error('a', 'b_c', exception)
    assert tracker.healthy == False
