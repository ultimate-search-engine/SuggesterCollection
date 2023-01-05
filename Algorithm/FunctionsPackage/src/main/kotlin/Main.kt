import kotlin.system.exitProcess
import use.algorithm.exanys.database.Elastic

suspend fun main() {
    val client = Elastic(9200, "localhost")
    println(client.getIds("ency"))
    exitProcess(0)
}