package use.algorithm.exanys.database

import com.jillesvangurp.ktsearch.KtorRestClient
import com.jillesvangurp.ktsearch.SearchClient
import com.jillesvangurp.ktsearch.ids
import com.jillesvangurp.ktsearch.search

class Elastic(port: Number, host: String) {
    val client = SearchClient()

    //    fun getTermVectors(index: String, id: String) {
//        val resp = client.search(index) {
//            termVectors {
//                ids(id)
//            }
//        }.ids
//    }
    suspend fun getIds(index: String): List<String> {
        return client.search(index).ids
    }
}