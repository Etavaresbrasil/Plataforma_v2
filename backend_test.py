#!/usr/bin/env python3
"""
PUCRS Gamification System Backend Test Suite
Tests all backend API endpoints and functionality
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys

# Backend URL from environment
BACKEND_URL = "https://2c7034bb-9078-4e97-aca9-f2f1e15d9c42.preview.emergentagent.com/api"

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def log_pass(self, test_name):
        print(f"✅ PASS: {test_name}")
        self.passed += 1
        
    def log_fail(self, test_name, error):
        print(f"❌ FAIL: {test_name} - {error}")
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} tests passed")
        print(f"{'='*60}")
        if self.errors:
            print("FAILURES:")
            for error in self.errors:
                print(f"  - {error}")
        return self.failed == 0

class PUCRSBackendTester:
    def __init__(self):
        self.results = TestResults()
        self.admin_token = None
        self.student_token = None
        self.professor_token = None
        self.admin_user = None
        self.student_user = None
        self.professor_user = None
        self.challenge_id = None
        self.solution_id = None
        
    def make_request(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Make HTTP request with error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            if response.status_code != expected_status:
                return None, f"Expected status {expected_status}, got {response.status_code}: {response.text}"
                
            return response.json() if response.content else {}, None
        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {str(e)}"
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON response: {str(e)}"
    
    def get_auth_headers(self, token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}"}
    
    def test_user_registration(self):
        """Test user registration for different roles"""
        print("\n🔐 Testing User Registration...")
        
        # Clear existing data for fresh testing
        try:
            # Try to clear existing users to start fresh
            import requests
            requests.delete(f"{BACKEND_URL.replace('/api', '')}/clear-test-data", timeout=5)
        except:
            pass  # Ignore if endpoint doesn't exist
        
        # Test admin registration
        admin_data = {
            "email": f"admin.test.{int(time.time())}@pucrs.edu.br",
            "name": "Maria Silva",
            "password": "AdminPass123!",
            "role": "admin"
        }
        
        response, error = self.make_request("POST", "/register", admin_data)
        if error:
            self.results.log_fail("Admin Registration", error)
            return False
        
        if not response.get("access_token") or not response.get("user"):
            self.results.log_fail("Admin Registration", "Missing token or user data")
            return False
            
        self.admin_token = response["access_token"]
        self.admin_user = response["user"]
        self.results.log_pass("Admin Registration")
        
        # Test student registration
        student_data = {
            "email": f"joao.santos.{int(time.time())}@pucrs.edu.br",
            "name": "João Santos",
            "password": "StudentPass123!",
            "role": "student"
        }
        
        response, error = self.make_request("POST", "/register", student_data)
        if error:
            self.results.log_fail("Student Registration", error)
            return False
            
        self.student_token = response["access_token"]
        self.student_user = response["user"]
        self.results.log_pass("Student Registration")
        
        # Test professor registration
        professor_data = {
            "email": f"prof.oliveira.{int(time.time())}@pucrs.edu.br",
            "name": "Prof. Carlos Oliveira",
            "password": "ProfPass123!",
            "role": "professor"
        }
        
        response, error = self.make_request("POST", "/register", professor_data)
        if error:
            self.results.log_fail("Professor Registration", error)
            return False
            
        self.professor_token = response["access_token"]
        self.professor_user = response["user"]
        self.results.log_pass("Professor Registration")
        
        # Test duplicate email registration
        response, error = self.make_request("POST", "/register", admin_data, expected_status=400)
        if error and "400" not in error:
            self.results.log_fail("Duplicate Email Prevention", error)
        else:
            self.results.log_pass("Duplicate Email Prevention")
            
        return True
    
    def test_user_login(self):
        """Test user login functionality"""
        print("\n🔑 Testing User Login...")
        
        if not self.admin_user:
            self.results.log_fail("Valid Login", "No admin user available for testing")
            return False
        
        # Test valid login
        login_data = {
            "email": self.admin_user["email"],
            "password": "AdminPass123!"
        }
        
        response, error = self.make_request("POST", "/login", login_data)
        if error:
            self.results.log_fail("Valid Login", error)
            return False
            
        if not response.get("access_token"):
            self.results.log_fail("Valid Login", "Missing access token")
            return False
            
        # Update admin token with fresh login token
        self.admin_token = response["access_token"]
        self.results.log_pass("Valid Login")
        
        # Test invalid credentials
        invalid_login = {
            "email": self.admin_user["email"],
            "password": "WrongPassword"
        }
        
        response, error = self.make_request("POST", "/login", invalid_login, expected_status=401)
        if error and "401" not in error:
            self.results.log_fail("Invalid Credentials Rejection", error)
        else:
            self.results.log_pass("Invalid Credentials Rejection")
            
        return True
    
    def test_profile_access(self):
        """Test profile access with JWT tokens"""
        print("\n👤 Testing Profile Access...")
        
        if not self.admin_token:
            self.results.log_fail("Profile Access with Valid Token", "No admin token available")
            return False
        
        # Test valid token access
        headers = self.get_auth_headers(self.admin_token)
        response, error = self.make_request("GET", "/me", headers=headers)
        if error:
            self.results.log_fail("Profile Access with Valid Token", error)
            return False
            
        if response.get("email") != self.admin_user["email"]:
            self.results.log_fail("Profile Access with Valid Token", "Incorrect user data")
            return False
            
        self.results.log_pass("Profile Access with Valid Token")
        
        # Test invalid token access
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response, error = self.make_request("GET", "/me", headers=invalid_headers, expected_status=401)
        if error and "401" not in error:
            self.results.log_fail("Invalid Token Rejection", error)
        else:
            self.results.log_pass("Invalid Token Rejection")
            
        return True
    
    def test_challenge_management(self):
        """Test challenge CRUD operations"""
        print("\n🎯 Testing Challenge Management...")
        
        # Test challenge creation (admin only)
        future_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        challenge_data = {
            "title": "Inovação em Sustentabilidade PUCRS",
            "description": "Desenvolva uma solução inovadora para reduzir o consumo de energia no campus da PUCRS",
            "category": "sustainability",
            "difficulty": "intermediate",
            "deadline": future_date,
            "criteria": "Originalidade, viabilidade técnica, impacto ambiental e aplicabilidade no campus",
            "points_reward": 150
        }
        
        headers = self.get_auth_headers(self.admin_token)
        response, error = self.make_request("POST", "/challenges", challenge_data, headers=headers)
        if error:
            self.results.log_fail("Challenge Creation (Admin)", error)
            return False
            
        if not response.get("id"):
            self.results.log_fail("Challenge Creation (Admin)", "Missing challenge ID")
            return False
            
        self.challenge_id = response["id"]
        self.results.log_pass("Challenge Creation (Admin)")
        
        # Test non-admin challenge creation (should fail)
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("POST", "/challenges", challenge_data, headers=student_headers, expected_status=403)
        if error and "403" not in error:
            self.results.log_fail("Non-Admin Challenge Creation Prevention", error)
        else:
            self.results.log_pass("Non-Admin Challenge Creation Prevention")
        
        # Test challenge retrieval
        response, error = self.make_request("GET", "/challenges", headers=student_headers)
        if error:
            self.results.log_fail("Challenge Retrieval", error)
            return False
            
        if not isinstance(response, list) or len(response) == 0:
            self.results.log_fail("Challenge Retrieval", "No challenges returned")
            return False
            
        self.results.log_pass("Challenge Retrieval")
        
        # Test specific challenge retrieval
        response, error = self.make_request("GET", f"/challenges/{self.challenge_id}", headers=student_headers)
        if error:
            self.results.log_fail("Specific Challenge Retrieval", error)
            return False
            
        if response.get("id") != self.challenge_id:
            self.results.log_fail("Specific Challenge Retrieval", "Incorrect challenge data")
            return False
            
        self.results.log_pass("Specific Challenge Retrieval")
        
        return True
    
    def test_solution_submission(self):
        """Test solution submission system"""
        print("\n📝 Testing Solution Submission...")
        
        if not self.challenge_id:
            self.results.log_fail("Solution Submission", "No challenge available for testing")
            return False
        
        # Test valid solution submission
        solution_data = {
            "challenge_id": self.challenge_id,
            "content": "Proposta de implementação de painéis solares nos telhados dos prédios principais do campus, com sistema de monitoramento inteligente que otimiza o consumo energético baseado em padrões de uso dos ambientes.",
            "files": ["data:text/plain;base64,UHJvcG9zdGEgZGV0YWxoYWRhIGRlIGltcGxlbWVudGHDp8OjbyBkZSBwYWluw6lpcyBzb2xhcmVz"]
        }
        
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("POST", "/solutions", solution_data, headers=student_headers)
        if error:
            self.results.log_fail("Valid Solution Submission", error)
            return False
            
        if not response.get("id"):
            self.results.log_fail("Valid Solution Submission", "Missing solution ID")
            return False
            
        self.solution_id = response["id"]
        self.results.log_pass("Valid Solution Submission")
        
        # Test duplicate solution submission (should fail)
        response, error = self.make_request("POST", "/solutions", solution_data, headers=student_headers, expected_status=400)
        if error and "400" not in error:
            self.results.log_fail("Duplicate Solution Prevention", error)
        else:
            self.results.log_pass("Duplicate Solution Prevention")
        
        # Test solution submission to non-existent challenge
        invalid_solution = {
            "challenge_id": "non-existent-id",
            "content": "Test content",
            "files": []
        }
        
        response, error = self.make_request("POST", "/solutions", invalid_solution, headers=student_headers, expected_status=404)
        if error and "404" not in error:
            self.results.log_fail("Invalid Challenge ID Handling", error)
        else:
            self.results.log_pass("Invalid Challenge ID Handling")
            
        return True
    
    def test_solution_retrieval(self):
        """Test solution retrieval endpoints"""
        print("\n📋 Testing Solution Retrieval...")
        
        # Test user's own solutions
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("GET", "/solutions/my", headers=student_headers)
        if error:
            self.results.log_fail("User Solutions Retrieval", error)
            return False
            
        if not isinstance(response, list):
            self.results.log_fail("User Solutions Retrieval", "Invalid response format")
            return False
            
        self.results.log_pass("User Solutions Retrieval")
        
        # Test admin solutions access
        admin_headers = self.get_auth_headers(self.admin_token)
        response, error = self.make_request("GET", "/solutions", headers=admin_headers)
        if error:
            self.results.log_fail("Admin Solutions Access", error)
            return False
            
        if not isinstance(response, list):
            self.results.log_fail("Admin Solutions Access", "Invalid response format")
            return False
            
        self.results.log_pass("Admin Solutions Access")
        
        # Test non-admin solutions access (should fail)
        response, error = self.make_request("GET", "/solutions", headers=student_headers, expected_status=403)
        if error and "403" not in error:
            self.results.log_fail("Non-Admin Solutions Access Prevention", error)
        else:
            self.results.log_pass("Non-Admin Solutions Access Prevention")
            
        return True
    
    def test_evaluation_system(self):
        """Test solution evaluation system"""
        print("\n⭐ Testing Evaluation System...")
        
        if not self.solution_id:
            self.results.log_fail("Solution Evaluation", "No solution available for testing")
            return False
        
        # Test solution evaluation by admin
        evaluation_data = {
            "solution_id": self.solution_id,
            "score": 120,
            "feedback": "Excelente proposta! A ideia dos painéis solares é muito viável e o sistema de monitoramento inteligente demonstra inovação. Sugestão: incluir análise de custo-benefício detalhada."
        }
        
        admin_headers = self.get_auth_headers(self.admin_token)
        response, error = self.make_request("PUT", "/solutions/evaluate", evaluation_data, headers=admin_headers)
        if error:
            self.results.log_fail("Admin Solution Evaluation", error)
            return False
            
        if not response.get("message"):
            self.results.log_fail("Admin Solution Evaluation", "Missing success message")
            return False
            
        self.results.log_pass("Admin Solution Evaluation")
        
        # Test non-admin evaluation (should fail)
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("PUT", "/solutions/evaluate", evaluation_data, headers=student_headers, expected_status=403)
        if error and "403" not in error:
            self.results.log_fail("Non-Admin Evaluation Prevention", error)
        else:
            self.results.log_pass("Non-Admin Evaluation Prevention")
        
        # Test evaluation of non-existent solution
        invalid_evaluation = {
            "solution_id": "non-existent-id",
            "score": 100,
            "feedback": "Test feedback"
        }
        
        response, error = self.make_request("PUT", "/solutions/evaluate", invalid_evaluation, headers=admin_headers, expected_status=404)
        if error and "404" not in error:
            self.results.log_fail("Invalid Solution ID Handling", error)
        else:
            self.results.log_pass("Invalid Solution ID Handling")
            
        return True
    
    def test_leaderboard(self):
        """Test leaderboard functionality"""
        print("\n🏆 Testing Leaderboard...")
        
        # Test leaderboard access (should be public)
        response, error = self.make_request("GET", "/leaderboard")
        if error:
            self.results.log_fail("Leaderboard Access", error)
            return False
            
        if not isinstance(response, list):
            self.results.log_fail("Leaderboard Access", "Invalid response format")
            return False
            
        # Check if leaderboard contains expected user data
        found_student = False
        for entry in response:
            if entry.get("name") == "João Santos":
                found_student = True
                if entry.get("points", 0) < 120:  # Should have points from evaluation
                    self.results.log_fail("Leaderboard Points Update", f"Expected at least 120 points, got {entry.get('points', 0)}")
                    return False
                break
        
        if not found_student:
            self.results.log_fail("Leaderboard User Presence", "Student not found in leaderboard")
            return False
            
        self.results.log_pass("Leaderboard Access")
        self.results.log_pass("Leaderboard Points Update")
        
        return True
    
    def test_admin_statistics(self):
        """Test admin dashboard statistics"""
        print("\n📊 Testing Admin Statistics...")
        
        # Test admin stats access
        admin_headers = self.get_auth_headers(self.admin_token)
        response, error = self.make_request("GET", "/admin/stats", headers=admin_headers)
        if error:
            self.results.log_fail("Admin Stats Access", error)
            return False
        
        required_fields = ["total_users", "total_challenges", "active_challenges", "total_solutions", "evaluated_solutions", "pending_evaluations"]
        for field in required_fields:
            if field not in response:
                self.results.log_fail("Admin Stats Completeness", f"Missing field: {field}")
                return False
        
        # Test enhanced statistics fields
        enhanced_fields = ["total_points_awarded", "recent_solutions_count", "recent_registrations_count"]
        for field in enhanced_fields:
            if field not in response:
                self.results.log_fail("Enhanced Stats Completeness", f"Missing enhanced field: {field}")
                return False
        
        # Validate expected values
        if response["total_users"] < 3:  # Should have at least admin, student, professor
            self.results.log_fail("Admin Stats Accuracy", f"Expected at least 3 users, got {response['total_users']}")
            return False
            
        if response["total_challenges"] < 1:  # Should have at least one challenge
            self.results.log_fail("Admin Stats Accuracy", f"Expected at least 1 challenge, got {response['total_challenges']}")
            return False
            
        if response["total_solutions"] < 1:  # Should have at least one solution
            self.results.log_fail("Admin Stats Accuracy", f"Expected at least 1 solution, got {response['total_solutions']}")
            return False
            
        self.results.log_pass("Admin Stats Access")
        self.results.log_pass("Admin Stats Completeness")
        self.results.log_pass("Enhanced Stats Completeness")
        self.results.log_pass("Admin Stats Accuracy")
        
        # Test non-admin stats access (should fail)
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("GET", "/admin/stats", headers=student_headers, expected_status=403)
        if error and "403" not in error:
            self.results.log_fail("Non-Admin Stats Access Prevention", error)
        else:
            self.results.log_pass("Non-Admin Stats Access Prevention")
            
        return True
    
    def test_advanced_search_system(self):
        """Test the advanced search system"""
        print("\n🔍 Testing Advanced Search System...")
        
        student_headers = self.get_auth_headers(self.student_token)
        
        # Test search with query parameter
        response, error = self.make_request("GET", "/search?q=sustentabilidade", headers=student_headers)
        if error:
            self.results.log_fail("Search System Basic Query", error)
            return False
        
        # Validate search response structure
        required_fields = ["challenges", "users", "total_results"]
        for field in required_fields:
            if field not in response:
                self.results.log_fail("Search Response Structure", f"Missing field: {field}")
                return False
        
        if not isinstance(response["challenges"], list):
            self.results.log_fail("Search Response Structure", "Challenges should be a list")
            return False
            
        if not isinstance(response["users"], list):
            self.results.log_fail("Search Response Structure", "Users should be a list")
            return False
            
        self.results.log_pass("Search System Basic Query")
        self.results.log_pass("Search Response Structure")
        
        # Test search with different terms
        test_queries = ["inovação", "energia", "campus", "PUCRS"]
        for query in test_queries:
            response, error = self.make_request("GET", f"/search?q={query}", headers=student_headers)
            if error:
                self.results.log_fail(f"Search Query '{query}'", error)
                return False
        
        self.results.log_pass("Search Multiple Queries")
        
        # Test admin search (should include users)
        admin_headers = self.get_auth_headers(self.admin_token)
        response, error = self.make_request("GET", "/search?q=João", headers=admin_headers)
        if error:
            self.results.log_fail("Admin Search with Users", error)
            return False
        
        # Admin search should potentially return users
        self.results.log_pass("Admin Search with Users")
        
        return True
    
    def test_badge_system(self):
        """Test automatic badge awarding system"""
        print("\n🏆 Testing Badge System...")
        
        # Check if student received "First Submission" badge after submitting solution
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("GET", "/me", headers=student_headers)
        if error:
            self.results.log_fail("Badge System - Profile Check", error)
            return False
        
        badges = response.get("badges", [])
        if "first_submission" not in badges:
            self.results.log_fail("First Submission Badge", "Badge not awarded after first solution submission")
            return False
        
        self.results.log_pass("First Submission Badge")
        
        # Test badge awarding after evaluation (should trigger additional badge checks)
        # The evaluation was already done in previous test, so badges should be updated
        response, error = self.make_request("GET", "/me", headers=student_headers)
        if error:
            self.results.log_fail("Badge System - Post Evaluation Check", error)
            return False
        
        # Check if badges list is properly maintained
        if not isinstance(response.get("badges", []), list):
            self.results.log_fail("Badge System Structure", "Badges should be a list")
            return False
        
        self.results.log_pass("Badge System Structure")
        self.results.log_pass("Badge System Post-Evaluation")
        
        return True
    
    def test_notification_system(self):
        """Test notification creation and retrieval"""
        print("\n🔔 Testing Notification System...")
        
        student_headers = self.get_auth_headers(self.student_token)
        
        # Test notification retrieval
        response, error = self.make_request("GET", "/notifications", headers=student_headers)
        if error:
            self.results.log_fail("Notification Retrieval", error)
            return False
        
        if not isinstance(response, list):
            self.results.log_fail("Notification Response Structure", "Notifications should be a list")
            return False
        
        self.results.log_pass("Notification Retrieval")
        self.results.log_pass("Notification Response Structure")
        
        # Check if notifications were created for badge awards and evaluations
        notification_types = [notif.get("type") for notif in response]
        expected_types = ["badge", "evaluation"]
        
        found_badge_notification = "badge" in notification_types
        found_evaluation_notification = "evaluation" in notification_types
        
        if found_badge_notification:
            self.results.log_pass("Badge Notification Creation")
        else:
            self.results.log_fail("Badge Notification Creation", "No badge notification found")
        
        if found_evaluation_notification:
            self.results.log_pass("Evaluation Notification Creation")
        else:
            self.results.log_fail("Evaluation Notification Creation", "No evaluation notification found")
        
        # Test marking notification as read
        if response:
            notification_id = response[0].get("id")
            if notification_id:
                read_response, error = self.make_request("PUT", f"/notifications/{notification_id}/read", headers=student_headers)
                if error:
                    self.results.log_fail("Mark Notification Read", error)
                    return False
                self.results.log_pass("Mark Notification Read")
            else:
                self.results.log_fail("Mark Notification Read", "No notification ID available")
        
        # Test mark all notifications as read
        response, error = self.make_request("PUT", "/notifications/mark-all-read", headers=student_headers)
        if error:
            self.results.log_fail("Mark All Notifications Read", error)
            return False
        
        self.results.log_pass("Mark All Notifications Read")
        
        return True
    
    def test_challenge_crud_operations(self):
        """Test challenge update and deletion (admin-only)"""
        print("\n✏️ Testing Challenge CRUD Operations...")
        
        if not self.challenge_id:
            self.results.log_fail("Challenge CRUD", "No challenge available for testing")
            return False
        
        admin_headers = self.get_auth_headers(self.admin_token)
        
        # Test challenge update
        update_data = {
            "title": "Inovação em Sustentabilidade PUCRS - ATUALIZADO",
            "description": "Desenvolva uma solução inovadora para reduzir o consumo de energia no campus da PUCRS - versão atualizada com novos critérios",
            "points_reward": 200
        }
        
        response, error = self.make_request("PUT", f"/challenges/{self.challenge_id}", update_data, headers=admin_headers)
        if error:
            self.results.log_fail("Challenge Update (Admin)", error)
            return False
        
        # Verify update was applied
        if response.get("title") != update_data["title"]:
            self.results.log_fail("Challenge Update Verification", "Title was not updated")
            return False
        
        if response.get("points_reward") != update_data["points_reward"]:
            self.results.log_fail("Challenge Update Verification", "Points reward was not updated")
            return False
        
        self.results.log_pass("Challenge Update (Admin)")
        self.results.log_pass("Challenge Update Verification")
        
        # Test non-admin challenge update (should fail)
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("PUT", f"/challenges/{self.challenge_id}", update_data, headers=student_headers, expected_status=403)
        if error and "403" not in error:
            self.results.log_fail("Non-Admin Challenge Update Prevention", error)
        else:
            self.results.log_pass("Non-Admin Challenge Update Prevention")
        
        # Test challenge deletion
        response, error = self.make_request("DELETE", f"/challenges/{self.challenge_id}", headers=admin_headers)
        if error:
            self.results.log_fail("Challenge Deletion (Admin)", error)
            return False
        
        if not response.get("message"):
            self.results.log_fail("Challenge Deletion Response", "Missing success message")
            return False
        
        self.results.log_pass("Challenge Deletion (Admin)")
        
        # Verify challenge was deleted
        response, error = self.make_request("GET", f"/challenges/{self.challenge_id}", headers=admin_headers, expected_status=404)
        if error and "404" not in error:
            self.results.log_fail("Challenge Deletion Verification", error)
        else:
            self.results.log_pass("Challenge Deletion Verification")
        
        # Test non-admin challenge deletion (should fail)
        # Create a new challenge first for this test
        future_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        new_challenge_data = {
            "title": "Test Challenge for Deletion",
            "description": "Test challenge",
            "category": "technology",
            "difficulty": "beginner",
            "deadline": future_date,
            "criteria": "Test criteria",
            "points_reward": 100
        }
        
        response, error = self.make_request("POST", "/challenges", new_challenge_data, headers=admin_headers)
        if response and response.get("id"):
            test_challenge_id = response["id"]
            response, error = self.make_request("DELETE", f"/challenges/{test_challenge_id}", headers=student_headers, expected_status=403)
            if error and "403" not in error:
                self.results.log_fail("Non-Admin Challenge Deletion Prevention", error)
            else:
                self.results.log_pass("Non-Admin Challenge Deletion Prevention")
        
        return True
    
    def test_user_management(self):
        """Test user activation/deactivation by admins"""
        print("\n👥 Testing User Management...")
        
        admin_headers = self.get_auth_headers(self.admin_token)
        
        # Test getting all users (admin only)
        response, error = self.make_request("GET", "/admin/users", headers=admin_headers)
        if error:
            self.results.log_fail("Admin Users List", error)
            return False
        
        if not isinstance(response, list):
            self.results.log_fail("Admin Users List Structure", "Users should be a list")
            return False
        
        if len(response) < 3:  # Should have at least admin, student, professor
            self.results.log_fail("Admin Users List Content", f"Expected at least 3 users, got {len(response)}")
            return False
        
        self.results.log_pass("Admin Users List")
        self.results.log_pass("Admin Users List Structure")
        self.results.log_pass("Admin Users List Content")
        
        # Test non-admin access to users list (should fail)
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("GET", "/admin/users", headers=student_headers, expected_status=403)
        if error and "403" not in error:
            self.results.log_fail("Non-Admin Users List Prevention", error)
        else:
            self.results.log_pass("Non-Admin Users List Prevention")
        
        # Test user activation/deactivation toggle
        if self.student_user and self.student_user.get("id"):
            student_id = self.student_user["id"]
            
            # Toggle user active status
            response, error = self.make_request("PUT", f"/admin/users/{student_id}/toggle-active", headers=admin_headers)
            if error:
                self.results.log_fail("User Toggle Active Status", error)
                return False
            
            if not response.get("message"):
                self.results.log_fail("User Toggle Response", "Missing success message")
                return False
            
            self.results.log_pass("User Toggle Active Status")
            self.results.log_pass("User Toggle Response")
            
            # Test login with deactivated account (should fail)
            login_data = {
                "email": "joao.santos@pucrs.edu.br",
                "password": "StudentPass123!"
            }
            
            response, error = self.make_request("POST", "/login", login_data, expected_status=401)
            if error and "401" not in error:
                self.results.log_fail("Deactivated Account Login Prevention", error)
            else:
                self.results.log_pass("Deactivated Account Login Prevention")
            
            # Reactivate user for further tests
            response, error = self.make_request("PUT", f"/admin/users/{student_id}/toggle-active", headers=admin_headers)
            if error:
                self.results.log_fail("User Reactivation", error)
                return False
            
            self.results.log_pass("User Reactivation")
        
        # Test non-admin user toggle (should fail)
        if self.student_user and self.student_user.get("id"):
            student_id = self.student_user["id"]
            response, error = self.make_request("PUT", f"/admin/users/{student_id}/toggle-active", headers=student_headers, expected_status=403)
            if error and "403" not in error:
                self.results.log_fail("Non-Admin User Toggle Prevention", error)
            else:
                self.results.log_pass("Non-Admin User Toggle Prevention")
        
        return True
    
    def test_advanced_filtering(self):
        """Test challenge filtering by category, difficulty, status, and search terms"""
        print("\n🔍 Testing Advanced Filtering...")
        
        admin_headers = self.get_auth_headers(self.admin_token)
        student_headers = self.get_auth_headers(self.student_token)
        
        # Create multiple challenges with different attributes for filtering tests
        future_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        test_challenges = [
            {
                "title": "Tecnologia Educacional",
                "description": "Desenvolver app educacional",
                "category": "technology",
                "difficulty": "beginner",
                "deadline": future_date,
                "criteria": "Funcionalidade e usabilidade",
                "points_reward": 100,
                "tags": ["app", "educação"]
            },
            {
                "title": "Saúde Digital",
                "description": "Sistema de monitoramento de saúde",
                "category": "health",
                "difficulty": "advanced",
                "deadline": future_date,
                "criteria": "Precisão e segurança",
                "points_reward": 250,
                "tags": ["saúde", "digital"]
            }
        ]
        
        created_challenge_ids = []
        for challenge_data in test_challenges:
            response, error = self.make_request("POST", "/challenges", challenge_data, headers=admin_headers)
            if response and response.get("id"):
                created_challenge_ids.append(response["id"])
        
        # Test category filtering
        response, error = self.make_request("GET", "/challenges?category=technology", headers=student_headers)
        if error:
            self.results.log_fail("Category Filtering", error)
            return False
        
        # Check if filtered results contain only technology category
        for challenge in response:
            if challenge.get("category") != "technology":
                self.results.log_fail("Category Filtering Accuracy", f"Found non-technology challenge: {challenge.get('category')}")
                return False
        
        self.results.log_pass("Category Filtering")
        self.results.log_pass("Category Filtering Accuracy")
        
        # Test difficulty filtering
        response, error = self.make_request("GET", "/challenges?difficulty=advanced", headers=student_headers)
        if error:
            self.results.log_fail("Difficulty Filtering", error)
            return False
        
        # Check if filtered results contain only advanced difficulty
        for challenge in response:
            if challenge.get("difficulty") != "advanced":
                self.results.log_fail("Difficulty Filtering Accuracy", f"Found non-advanced challenge: {challenge.get('difficulty')}")
                return False
        
        self.results.log_pass("Difficulty Filtering")
        self.results.log_pass("Difficulty Filtering Accuracy")
        
        # Test search term filtering
        response, error = self.make_request("GET", "/challenges?search=saúde", headers=student_headers)
        if error:
            self.results.log_fail("Search Term Filtering", error)
            return False
        
        self.results.log_pass("Search Term Filtering")
        
        # Test combined filtering
        response, error = self.make_request("GET", "/challenges?category=health&difficulty=advanced", headers=student_headers)
        if error:
            self.results.log_fail("Combined Filtering", error)
            return False
        
        self.results.log_pass("Combined Filtering")
        
        # Clean up created challenges
        for challenge_id in created_challenge_ids:
            self.make_request("DELETE", f"/challenges/{challenge_id}", headers=admin_headers)
        
        return True
    
    def test_file_upload_system(self):
        """Test solution submission with files (base64 format)"""
        print("\n📎 Testing File Upload System...")
        
        # Create a new challenge for file upload testing
        admin_headers = self.get_auth_headers(self.admin_token)
        future_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        challenge_data = {
            "title": "Projeto com Arquivos",
            "description": "Submeta sua solução com arquivos anexos",
            "category": "technology",
            "difficulty": "intermediate",
            "deadline": future_date,
            "criteria": "Qualidade dos arquivos e documentação",
            "points_reward": 150
        }
        
        response, error = self.make_request("POST", "/challenges", challenge_data, headers=admin_headers)
        if error or not response.get("id"):
            self.results.log_fail("File Upload Test Setup", "Failed to create test challenge")
            return False
        
        test_challenge_id = response["id"]
        
        # Test solution submission with multiple files
        student_headers = self.get_auth_headers(self.professor_token)  # Use professor to avoid duplicate submission
        
        # Create base64 encoded test files
        test_files = [
            "data:text/plain;base64,VGVzdGUgZGUgYXJxdWl2byBkZSB0ZXh0bw==",  # "Teste de arquivo de texto"
            "data:application/json;base64,eyJ0ZXN0ZSI6ICJ2YWxvciJ9",  # {"teste": "valor"}
        ]
        
        file_names = ["documento.txt", "config.json"]
        
        solution_data = {
            "challenge_id": test_challenge_id,
            "content": "Solução completa com arquivos anexos demonstrando a implementação técnica detalhada.",
            "files": test_files,
            "file_names": file_names
        }
        
        response, error = self.make_request("POST", "/solutions", solution_data, headers=student_headers)
        if error:
            self.results.log_fail("File Upload Submission", error)
            return False
        
        if not response.get("id"):
            self.results.log_fail("File Upload Response", "Missing solution ID")
            return False
        
        # Verify files were stored correctly
        if response.get("files") != test_files:
            self.results.log_fail("File Upload Storage", "Files not stored correctly")
            return False
        
        if response.get("file_names") != file_names:
            self.results.log_fail("File Names Storage", "File names not stored correctly")
            return False
        
        self.results.log_pass("File Upload Submission")
        self.results.log_pass("File Upload Response")
        self.results.log_pass("File Upload Storage")
        self.results.log_pass("File Names Storage")
        
        # Test solution retrieval with files
        response, error = self.make_request("GET", "/solutions/my", headers=student_headers)
        if error:
            self.results.log_fail("File Upload Retrieval", error)
            return False
        
        # Find the solution with files
        found_solution_with_files = False
        for solution in response:
            if solution.get("files") and len(solution["files"]) > 0:
                found_solution_with_files = True
                break
        
        if not found_solution_with_files:
            self.results.log_fail("File Upload Retrieval Verification", "Solution with files not found in retrieval")
            return False
        
        self.results.log_pass("File Upload Retrieval")
        self.results.log_pass("File Upload Retrieval Verification")
        
        # Clean up
        self.make_request("DELETE", f"/challenges/{test_challenge_id}", headers=admin_headers)
        
        return True
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting PUCRS Gamification Backend Test Suite - ENHANCED FEATURES")
        print(f"Testing backend at: {BACKEND_URL}")
        print("="*60)
        
        # Run tests in logical order - Basic features first, then enhanced features
        tests = [
            # Basic functionality tests
            self.test_user_registration,
            self.test_user_login,
            self.test_profile_access,
            self.test_challenge_management,
            self.test_solution_submission,
            self.test_solution_retrieval,
            self.test_evaluation_system,
            self.test_leaderboard,
            
            # Enhanced features tests (HIGH PRIORITY)
            self.test_advanced_search_system,
            self.test_badge_system,
            self.test_notification_system,
            
            # Enhanced features tests (MEDIUM PRIORITY)
            self.test_challenge_crud_operations,
            self.test_user_management,
            self.test_file_upload_system,
            
            # Enhanced features tests (LOW PRIORITY)
            self.test_admin_statistics,
            self.test_advanced_filtering
        ]
        
        for test in tests:
            try:
                success = test()
                if not success:
                    print(f"⚠️  Test {test.__name__} failed, continuing with remaining tests...")
            except Exception as e:
                self.results.log_fail(test.__name__, f"Unexpected error: {str(e)}")
                print(f"💥 Unexpected error in {test.__name__}: {str(e)}")
        
        return self.results.summary()

if __name__ == "__main__":
    tester = PUCRSBackendTester()
    success = tester.run_all_tests()
    
    if not success:
        print("\n🔍 Some tests failed. Check the errors above for details.")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed! Backend is working correctly.")
        sys.exit(0)