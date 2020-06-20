from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from accounts.serializers import UserSerializer


class MyPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("request_user", UserSerializer(self.request.user).data),
                    ("results", data),
                ]
            )
        )
