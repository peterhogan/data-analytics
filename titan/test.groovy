import com.thinkaurelius.titan.core.TitanFactory
import com.thinkaurelius.titan.core.TitanVertex
import com.thinkaurelius.titan.core.TitanGraph
import com.thinkaurelius.titan.core.Cardinality
import com.thinkaurelius.titan.core.TitanTransaction
import org.apache.tinkerpop.gremlin.structure.T

println "hello titan"

graph = TitanFactory.open('/analytics/titan/titan-berkeleyje.properties')

mgmt = graph.openManagement()

// Schema
// Vertices
stationId = mgmt.makePropertyKey('stationId').dataType(Integer.class).cardinality(Cardinality.SINGLE).make()
stationIdIndex = mgmt.buildIndex('stationId', Vertex.class).addKey(stationId)

stationName = mgmt.makePropertyKey('stationName').dataType(String.class).make()
stationNameIndex = mgmt.buildIndex('stationName', Vertex.class).addKey(stationName)

zone = mgmt.makePropertyKey('zone').dataType(Float.class).make()
totalLines = mgmt.makePropertyKey('totalLines').dataType(Integer.class).make()
line = mgmt.makePropertyKey('line').dataType(String.class).make()

// Edges

mgmt.commit()

println "finished schema"

String stationsCSV = new File('/analytics/tinkerpop/stations.csv').text
String[] lines = stationsCSV.split('\n')
List<String[]> rows = lines.collect {it.split(',')}

//TitanTransaction tx = graph.newTransaction()

//for (item in rows.drop(1)) { println(item) }

List<TitanVertex> vertexList = new ArrayList<TitanVertex>()

for (String[] item : rows.drop(1)) {

    //println([item[0],item[3],item[5],item[6]])
    println "Adding Vertex ${item[0]}, with name ${item[3]}." 

    vertexList.add(graph.addVertex(T.label, item[0], 
            'stationId', item[0] as Integer, 
            'stationName', item[3],
            'zone', item[5] as Float,
            'totalLines', item[6] as Integer))

}

graph.tx().commit()

println "finished vertices"

g = graph.traversal()

String linesCSV = new File('/analytics/tinkerpop/lines.csv').text
String[] lines_lines = linesCSV.split('\n')
List<String[]> lines_rows = lines_lines.collect {it.split(',')}

for (item in lines_rows.drop(1)) {

    def v1 = g.V().has('stationId', item[0]).next()
    def v2 = g.V().has('stationId', item[1]).next()
    def Line = item[2]

    println "Adding Edge between ${v1.values('stationName')[0]} and ${v2.values('stationName')[0]}, on line ${Line}.\n"
    

    /*
    //println item
    def v1 = item[0]
    def v2 = item[1]
    def line = item[2]

    def V1 = graph.addVertex('stationId', v1, 'line', line)
    def V2 = graph.addVertex('stationId', v2, 'line', line)
    
    V1.addEdge('connected', V2)
    */
    
    
}
//println vertexList[0].values('stationId')[0]
//println vertexList[0].values('stationName')[0]

g = graph.traversal()


println "finished edges"

println "finished graph"

graph.close()
