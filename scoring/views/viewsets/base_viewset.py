from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from server.views import RequestFailed, RequestSuccess


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "size"
    max_page_size = 500

    def get_paginated_response(self, data):

        return RequestSuccess({
            "count": self.page.paginator.count,
            "pages": self.page.paginator.num_pages,
            "per_page": self.page.paginator.per_page,
            "elements": data
        })


class EmptyViewSet(viewsets.ModelViewSet):
    queryset = None

    @action(detail=False, url_path="empty", methods=["GET"])
    def empty(self, request=None):
        return RequestFailed()
