
import unittest
from unittest.mock import patch
from main import fetch_github_events, Session

class TestGitHubEventTracker(unittest.TestCase):

    @patch('github_event_tracker.requests.get')
    def test_fetch_github_events(self, mock_requests):
        # Mock the response from the GitHub API
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = [{'type': 'PushEvent', 'created_at': '2023-01-01T12:00:00Z'}]

        # Clear the database before running the test
        Session().query().delete()

        # Run the function
        fetch_github_events()

        # Verify that events are stored in the database
        session = Session()
        count = session.query().count()
        self.assertEqual(count, 1)

if __name__ == '__main__':
    unittest.main()
