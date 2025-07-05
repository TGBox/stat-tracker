import pytest

from modules.youtube_tracker import (
    get_channel_videos,
    get_video_stats,
    get_channel_subscribers,
    YoutubeTrackerError
)

def test_get_channel_videos_valid_channel(monkeypatch):
    def mock_api_call(channel_id):
        return [{'id': 'vid1'}, {'id': 'vid2'}]
    monkeypatch.setattr('..youtube_tracker._fetch_channel_videos', mock_api_call)
    videos = get_channel_videos('valid_channel')
    assert isinstance(videos, list)
    assert len(videos) == 2
    assert videos[0]['id'] == 'vid1'

def test_get_channel_videos_invalid_channel(monkeypatch):
    def mock_api_call(channel_id):
        raise YoutubeTrackerError("Channel not found")
    monkeypatch.setattr('..youtube_tracker._fetch_channel_videos', mock_api_call)
    with pytest.raises(YoutubeTrackerError):
        get_channel_videos('invalid_channel')

def test_get_video_stats_valid(monkeypatch):
    def mock_api_call(video_id):
        return {'views': 100, 'likes': 10, 'comments': 2}
    monkeypatch.setattr('..youtube_tracker._fetch_video_stats', mock_api_call)
    stats = get_video_stats('video123')
    assert stats['views'] == 100
    assert stats['likes'] == 10
    assert stats['comments'] == 2

def test_get_video_stats_invalid(monkeypatch):
    def mock_api_call(video_id):
        raise YoutubeTrackerError("Video not found")
    monkeypatch.setattr('..youtube_tracker._fetch_video_stats', mock_api_call)
    with pytest.raises(YoutubeTrackerError):
        get_video_stats('bad_video')

def test_get_channel_subscribers_valid(monkeypatch):
    def mock_api_call(channel_id):
        return 12345
    monkeypatch.setattr('..youtube_tracker._fetch_channel_subscribers', mock_api_call)
    subs = get_channel_subscribers('channelX')
    assert subs == 12345

def test_get_channel_subscribers_invalid(monkeypatch):
    def mock_api_call(channel_id):
        raise YoutubeTrackerError("Channel not found")
    monkeypatch.setattr('..youtube_tracker._fetch_channel_subscribers', mock_api_call)
    with pytest.raises(YoutubeTrackerError):
        get_channel_subscribers('bad_channel')