import pprint
import os
import time

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError
from elasticsearch_dsl import connections, DocType, FacetedSearch, TermsFacet
from elasticsearch_dsl.field import Keyword, Integer, Boolean


def _wait_elasticsearch_healthy():
    es = Elasticsearch('elasticsearch:9200')
    start = time.time()
    for _ in range(0, 120):
        try:
            es.cluster.health(wait_for_status='yellow')
            print('Elasticsearch took %d seconds to come up.' %
                                (time.time() - start))
            break
        except ConnectionError:
            print('Elasticsearch not up yet, will try again.')
            time.sleep(1)
    else:
        raise EnvironmentError("Elasticsearch failed to start.")


class Post(DocType):
    comment = Keyword()
    likes = Integer()
    published = Boolean()
    class Meta:
        index = 'blog'


class PostSearch(FacetedSearch):
    index = 'blog'
    doc_types = [Post]
    fields = 'comment', 'likes', 'published'
    facets = {k: TermsFacet(field=k) for k in fields}


_wait_elasticsearch_healthy()
connections.create_connection(hosts=['elasticsearch:9200'], timeout=20)
Post.init()
Post(comment='potato', likes=42, published=True).save()
Post(comment='spud', likes=12, published=False).save()
Post(comment='foo', likes=7, published=True).save()
search = PostSearch()
response = search.execute()
print('Actual response data is correct: ')
pprint.pprint(vars(response[0]))
print('Facet is incorrect: ')
pprint.pprint(response.facets.to_dict())
