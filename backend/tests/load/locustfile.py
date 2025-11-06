"""
Load testing script using Locust.

To run:
    pip install locust
    locust -f locustfile.py --host=http://localhost:8000

Then open http://localhost:8089 to configure and start the test.

For headless mode:
    locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 5m --headless
"""
from locust import HttpUser, task, between
import random
import uuid


class CultureBridgeUser(HttpUser):
    """Simulates a user interacting with the CultureBridge platform."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a simulated user starts."""
        self.token = None
        self.user_role = random.choice(["client", "coach"])
        self.signup_and_login()
    
    def signup_and_login(self):
        """Sign up and log in to get authentication token."""
        # Sign up
        email = f"loadtest_{uuid.uuid4()}@test.com"
        signup_data = {
            "email": email,
            "password": "TestPassword123!",
            "role": self.user_role
        }
        
        with self.client.post("/auth/signup", json=signup_data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 409:
                # User already exists, that's okay
                response.success()
            else:
                response.failure(f"Signup failed with status {response.status_code}")
        
        # Login
        login_data = {
            "email": email,
            "password": "TestPassword123!"
        }
        
        with self.client.post("/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.email = email
                response.success()
            else:
                response.failure(f"Login failed with status {response.status_code}")
    
    def get_headers(self):
        """Get authentication headers."""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    @task(5)
    def view_health(self):
        """Check health endpoint (high frequency)."""
        self.client.get("/health")
    
    @task(10)
    def list_coaches(self):
        """List coaches (high frequency)."""
        params = {
            "skip": random.randint(0, 20),
            "limit": 20
        }
        self.client.get("/coaches", params=params, headers=self.get_headers())
    
    @task(3)
    def view_coach_profile(self):
        """View a specific coach profile."""
        # First get list of coaches
        response = self.client.get("/coaches?limit=10", headers=self.get_headers())
        if response.status_code == 200:
            coaches = response.json().get("items", [])
            if coaches:
                coach_id = coaches[0]["id"]
                self.client.get(f"/coaches/{coach_id}", headers=self.get_headers())
    
    @task(2)
    def view_profile(self):
        """View own profile."""
        self.client.get("/profile", headers=self.get_headers())
    
    @task(1)
    def update_profile(self):
        """Update own profile."""
        if self.user_role == "client":
            profile_data = {
                "first_name": "Load",
                "last_name": "Test",
                "timezone": "America/New_York",
                "quiz_data": {
                    "target_countries": ["Spain"],
                    "goals": ["career_transition"],
                    "languages": ["English"],
                    "budget_max": 150
                }
            }
        else:  # coach
            profile_data = {
                "first_name": "Load",
                "last_name": "Test",
                "bio": "Test coach bio",
                "expertise": ["career_coaching"],
                "languages": ["English"],
                "countries": ["USA"],
                "hourly_rate": 100.00
            }
        
        self.client.put("/profile", json=profile_data, headers=self.get_headers())
    
    @task(3)
    def list_community_posts(self):
        """List community posts."""
        params = {
            "skip": random.randint(0, 20),
            "limit": 20
        }
        self.client.get("/community/posts", params=params, headers=self.get_headers())
    
    @task(1)
    def create_community_post(self):
        """Create a community post."""
        post_data = {
            "title": f"Load Test Post {uuid.uuid4()}",
            "content": "This is a test post created during load testing.",
            "post_type": "discussion",
            "is_private": False
        }
        self.client.post("/community/posts", json=post_data, headers=self.get_headers())
    
    @task(2)
    def list_resources(self):
        """List community resources."""
        params = {
            "skip": random.randint(0, 20),
            "limit": 20
        }
        self.client.get("/community/resources", params=params, headers=self.get_headers())


class ClientUser(HttpUser):
    """Simulates a client user specifically."""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Called when a simulated user starts."""
        self.token = None
        self.signup_and_login()
    
    def signup_and_login(self):
        """Sign up and log in as client."""
        email = f"client_{uuid.uuid4()}@test.com"
        signup_data = {
            "email": email,
            "password": "TestPassword123!",
            "role": "client"
        }
        
        self.client.post("/auth/signup", json=signup_data)
        
        login_data = {
            "email": email,
            "password": "TestPassword123!"
        }
        
        response = self.client.post("/auth/login", json=login_data)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
    
    def get_headers(self):
        """Get authentication headers."""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    @task(10)
    def browse_coaches(self):
        """Browse coaches with different filters."""
        filters = [
            {"language": "Spanish"},
            {"country": "Spain"},
            {"expertise": "career_coaching"},
            {"max_rate": 150},
            {}
        ]
        filter_params = random.choice(filters)
        filter_params.update({"skip": 0, "limit": 20})
        
        self.client.get("/coaches", params=filter_params, headers=self.get_headers())
    
    @task(5)
    def request_matches(self):
        """Request AI-powered coach matches."""
        match_data = {
            "force_refresh": False
        }
        self.client.post("/match", json=match_data, headers=self.get_headers())
    
    @task(2)
    def view_bookings(self):
        """View own bookings."""
        # This would need the actual client_id, simplified for load testing
        self.client.get("/booking/client/test", headers=self.get_headers())


class AdminUser(HttpUser):
    """Simulates an admin user."""
    
    wait_time = between(5, 10)
    
    def on_start(self):
        """Called when a simulated user starts."""
        self.token = None
        # In real scenario, admin would use existing credentials
        # For load testing, we'll create a test admin
        self.login_as_admin()
    
    def login_as_admin(self):
        """Login as admin (assumes admin user exists)."""
        login_data = {
            "email": "admin@test.com",
            "password": "Admin123!"
        }
        
        response = self.client.post("/auth/login", json=login_data)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
    
    def get_headers(self):
        """Get authentication headers."""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    @task(5)
    def view_metrics(self):
        """View platform metrics."""
        self.client.get("/admin/metrics", headers=self.get_headers())
    
    @task(3)
    def list_users(self):
        """List all users."""
        params = {
            "skip": random.randint(0, 50),
            "limit": 20
        }
        self.client.get("/admin/users", params=params, headers=self.get_headers())
    
    @task(2)
    def list_bookings(self):
        """List all bookings."""
        params = {
            "skip": random.randint(0, 50),
            "limit": 20
        }
        self.client.get("/admin/bookings", params=params, headers=self.get_headers())
    
    @task(1)
    def view_revenue(self):
        """View revenue reports."""
        params = {
            "start_date": "2025-10-01",
            "end_date": "2025-11-05"
        }
        self.client.get("/admin/revenue", params=params, headers=self.get_headers())
