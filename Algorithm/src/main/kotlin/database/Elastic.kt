package com.use.binar.algorithm.database

import com.jillesvangurp.ktsearch.KtorRestClient
import com.jillesvangurp.ktsearch.SearchClient

class Elastic(port: Number, host: String) {
    val client = SearchClient(KtorRestClient(host, port.toInt()))
}