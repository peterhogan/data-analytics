import com.thinkaurelius.titan.core.EdgeLabel
import com.thinkaurelius.titan.core.Multiplicity
import com.thinkaurelius.titan.core.PropertyKey
import com.thinkaurelius.titan.core.TitanFactory
/*import com.thinkaurelius.titan.core.TitanGraph
import com.thinkaurelius.titan.core.TitanTransaction
import com.thinkaurelius.titan.core.attribute.Geoshape
import com.thinkaurelius.titan.core.schema.ConsistencyModifier
import com.thinkaurelius.titan.core.schema.TitanGraphIndex
import com.thinkaurelius.titan.core.schema.TitanManagement
import org.apache.tinkerpop.gremlin.process.traversal.Order
import org.apache.tinkerpop.gremlin.structure.Direction
import org.apache.tinkerpop.gremlin.structure.Edge
import org.apache.tinkerpop.gremlin.structure.T
import org.apache.tinkerpop.gremlin.structure.Vertex
*/

graph = TitanFactory.open('conf/titan-berkeleyje-es.properties')

mgmt = graph.openManagement()
firstname = mgmt.makePropertyKey("firstname").dataType(String.class).make()
//mgmt.buildIndex("firstname", Vertex.class).addKey(firstname)
//age = mgmt.makePropertyKey("age").dataType(Integer.class).make()
//job = mgmt.makePropertyKey("job").dataType(String.class).make()
//population = mgmt.makePropertyKey("population").dataType(Integer.class).make()
//rela = makePropertyKey("rela").dataType(String.class).make()

mgmt.makeEdgeLabel("worksIn").multiplicity(Multiplicity.MANY2ONE).make()
mgmt.makeEdgeLabel("livesIn").multiplicity(Multiplicity.MANY2ONE).make()
mgmt.makeEdgeLabel("isIn").make()
mgmt.makeEdgeLabel("knows").make()
mgmt.makeEdgeLabel("isRelated").make()
mgmt.makeVertexLabel("person").make()
mgmt.makeVertexLabel("county").make()
mgmt.makeVertexLabel("country").make()
mgmt.commit()
/*
TitanTransaction tx = graph.newTransaction()

fish = tx.addVertex(T.label, "person", "firstname", "fish", "age", 26, "job", "swimmer")
gin = tx.addVertex(T.label, "person", "firstname", "gin", "age", 88, "job", "drinker")
hal = tx.addVertex(T.label, "person", "firstname", "hal", "age", 9000, "job", "computer")
lilly = tx.addVertex(T.label, "person", "firstname", "lilly", "age", 43, "job", "flower")
magenta = tx.addVertex(T.label, "person", "firstname", "magenta", "age", 20, "job", "wrapper")
nina = tx.addVertex(T.label, "person", "firstname", "nina", "age", 38, "job", "director-CTU")
orin = tx.addVertex(T.label, "person", "firstname", "orin", "age", 25, "job", "orange")
peeves = tx.addVertex(T.label, "person", "firstname", "peeves", "age", 28, "job", "bulter")
quentin = tx.addVertex(T.label, "person", "firstname", "quentin", "age", 67, "job", "writer")
siobhan = tx.addVertex(T.label, "person", "firstname", "siobhan", "age", 55, "job", "smoker")
teegan = tx.addVertex(T.label, "person", "firstname", "teegan", "age", 26, "job", "maiden")
uknown = tx.addVertex(T.label, "person", "firstname", "unknown", "age", 8, "job", "pokemon")
yveltel = tx.addVertex(T.label, "person", "firstname", "yveltel", "age", 89, "job", "pokemon")
zante = tx.addVertex(T.label, "person", "firstname", "zante", "age", 123, "job", "island")
uk = tx.addVertex(T.label, "country", "firstname", "UK")
greece = tx.addVertex(T.label, "country", "firstname", "Greece")
staffs = tx.addVertex(T.label, "county", "firstname", "staffs", "population", 30000)
berks = tx.addVertex(T.label, "county", "firstname", "berks", "population", 45000)
norfolk = tx.addVertex(T.label, "county", "firstname", "norfolk", "population", 15000)
herts = tx.addVertex(T.label, "county", "firstname", "herts", "population", 43000)
hants = tx.addVertex(T.label, "county", "firstname", "hants", "population", 60000);
// edges
fish.addEdge("worksIn", staffs)
fish.addEdge("livesIn", uk)
fish.addEdge("knows", gin)
fish.addEdge("isRelated", gin).property("rela", "father")
fish.addEdge("knows", hal)
fish.addEdge("isRelated", teegan).property("rela", "mother")
fish.addEdge("knows", teegan)

tx.commit()
*/
println "Finished"
graph.close()
