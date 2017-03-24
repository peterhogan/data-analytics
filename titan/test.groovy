import com.thinkaurelius.titan.core.TitanFactory
import com.thinkaurelius.titan.core.TitanGraph
import com.thinkaurelius.titan.core.Cardinality
import com.thinkaurelius.titan.core.TitanTransaction
import org.apache.tinkerpop.gremlin.structure.T

println "hello titan"

graph = TitanFactory.open('/analytics/titan-berkeleyje.properties')

mgmt = graph.openManagement()

stationId = mgmt.makePropertyKey('stationId').dataType(Integer.class).cardinality(Cardinality.SINGLE).make()
stationName = mgmt.makePropertyKey('stationName').dataType(String.class).make()
zone = mgmt.makePropertyKey('zone').dataType(Integer.class).make()
totalLines = mgmt.makePropertyKey('totalLines').dataType(Integer.class).make()
line = mgmt.makePropertyKey('line').dataType(String.class).make()

mgmt.commit()

String stationsCSV = new File('/data/stations.csv').text
String[] lines = stationsCSV.split('\n')
List<String[]> rows = lines.collect {it.split(',')}

TitanTransaction tx = graph.newTransaction()

for (String[] item : rows) {
    if ( item[0] == "id") {
        return
    }
    println([item[0],item[3],item[5],item[6]])
    println "Adding Vertex"
    tx.addVertex(T.label, item[0], 'name', item[3])
    
}

println "finished"

graph.close()
