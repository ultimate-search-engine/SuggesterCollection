package org.use.binar.algorithm.elastic

import co.elastic.clients.elasticsearch.ElasticsearchClient
import co.elastic.clients.json.jackson.JacksonJsonpMapper
import co.elastic.clients.transport.ElasticsearchTransport
import co.elastic.clients.transport.rest_client.RestClientTransport
import org.apache.http.HttpHost
import org.elasticsearch.client.RestClient


class Client(port: Int = 9200, host: String = "localhost") {
    val client: ElasticsearchClient

    init {
        val restClient: RestClient = RestClient.builder(
            HttpHost(host, port)
        ).build()
        val transport: ElasticsearchTransport = RestClientTransport(
            restClient, JacksonJsonpMapper()
        )
        client = ElasticsearchClient(transport)
    }
}