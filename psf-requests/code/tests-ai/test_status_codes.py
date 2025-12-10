"""
Tests for requests.status_codes module.
"""
import pytest

from requests.status_codes import codes


class TestStatusCodes:
    """Tests for status codes lookup."""
    
    def test_ok_status_code(self):
        """Should have ok status code."""
        assert codes.ok == 200
        assert codes.OK == 200
        assert codes.okay == 200
    
    def test_created_status_code(self):
        """Should have created status code."""
        assert codes.created == 201
    
    def test_accepted_status_code(self):
        """Should have accepted status code."""
        assert codes.accepted == 202
    
    def test_no_content_status_code(self):
        """Should have no_content status code."""
        assert codes.no_content == 204
    
    def test_moved_permanently_status_code(self):
        """Should have moved_permanently status code."""
        assert codes.moved_permanently == 301
        assert codes.moved == 301
    
    def test_found_status_code(self):
        """Should have found status code."""
        assert codes.found == 302
    
    def test_see_other_status_code(self):
        """Should have see_other status code."""
        assert codes.see_other == 303
    
    def test_not_modified_status_code(self):
        """Should have not_modified status code."""
        assert codes.not_modified == 304
    
    def test_temporary_redirect_status_code(self):
        """Should have temporary_redirect status code."""
        assert codes.temporary_redirect == 307
    
    def test_permanent_redirect_status_code(self):
        """Should have permanent_redirect status code."""
        assert codes.permanent_redirect == 308
    
    def test_bad_request_status_code(self):
        """Should have bad_request status code."""
        assert codes.bad_request == 400
        assert codes.bad == 400
    
    def test_unauthorized_status_code(self):
        """Should have unauthorized status code."""
        assert codes.unauthorized == 401
    
    def test_forbidden_status_code(self):
        """Should have forbidden status code."""
        assert codes.forbidden == 403
    
    def test_not_found_status_code(self):
        """Should have not_found status code."""
        assert codes.not_found == 404
    
    def test_method_not_allowed_status_code(self):
        """Should have method_not_allowed status code."""
        assert codes.method_not_allowed == 405
    
    def test_request_timeout_status_code(self):
        """Should have request_timeout status code."""
        assert codes.request_timeout == 408
        assert codes.timeout == 408
    
    def test_conflict_status_code(self):
        """Should have conflict status code."""
        assert codes.conflict == 409
    
    def test_teapot_status_code(self):
        """Should have teapot status code."""
        assert codes.teapot == 418
        assert codes.im_a_teapot == 418
    
    def test_too_many_requests_status_code(self):
        """Should have too_many_requests status code."""
        assert codes.too_many_requests == 429
    
    def test_internal_server_error_status_code(self):
        """Should have internal_server_error status code."""
        assert codes.internal_server_error == 500
        assert codes.server_error == 500
    
    def test_not_implemented_status_code(self):
        """Should have not_implemented status code."""
        assert codes.not_implemented == 501
    
    def test_bad_gateway_status_code(self):
        """Should have bad_gateway status code."""
        assert codes.bad_gateway == 502
    
    def test_service_unavailable_status_code(self):
        """Should have service_unavailable status code."""
        assert codes.service_unavailable == 503
    
    def test_gateway_timeout_status_code(self):
        """Should have gateway_timeout status code."""
        assert codes.gateway_timeout == 504
    
    def test_case_insensitive_attribute_access(self):
        """Should support both lowercase and uppercase."""
        assert codes.ok == codes.OK
        assert codes.not_found == codes.NOT_FOUND
    
    def test_getitem_access(self):
        """Should support dict-like access."""
        assert codes['ok'] == 200
        assert codes['not_found'] == 404
    
    def test_get_method(self):
        """Should support get() method."""
        assert codes.get('ok') == 200
        assert codes.get('nonexistent') is None
    
    def test_get_with_default(self):
        """get() should return default for missing codes."""
        assert codes.get('nonexistent', 999) == 999
