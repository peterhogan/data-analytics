import com.thinkaurelius.titan.core.EdgeLabel
import com.thinkaurelius.titan.core.Multiplicity
import com.thinkaurelius.titan.core.PropertyKey
import com.thinkaurelius.titan.core.TitanFactory
import com.thinkaurelius.titan.core.TitanGraph
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

//graph = TitanFactory.open('conf/titan-berkeleyje-es.properties')
//graph = TitanFactory.open('/analytics/titan/graphtest.properties')
graph = TitanFactory.open('/analytics/titan-berkeleyje.properties')

mgmt = graph.openManagement()
name = mgmt.makePropertyKey("name").dataType(String.class).make()
//mgmt.buildIndex("name", Vertex.class).addKey(name)
age = mgmt.makePropertyKey("age").dataType(Integer.class).make()
job = mgmt.makePropertyKey("job").dataType(String.class).make()
population = mgmt.makePropertyKey("population").dataType(Integer.class).make()
rela = mgmt.makePropertyKey("rela").dataType(String.class).make()

mgmt.makeEdgeLabel("worksIn").multiplicity(Multiplicity.MANY2ONE).make()
mgmt.makeEdgeLabel("livesIn").multiplicity(Multiplicity.MANY2ONE).make()
mgmt.makeEdgeLabel("isIn").make()
mgmt.makeEdgeLabel("knows").make()
mgmt.makeEdgeLabel("isRelated").make()
mgmt.makeVertexLabel("person").make()
mgmt.makeVertexLabel("county").make()
mgmt.makeVertexLabel("country").make()
mgmt.commit()

TitanTransaction tx = graph.newTransaction()

fish = tx.addVertex(T.label, "person", "name", "fish", "age", 26, "job", "swimmer")
gin = tx.addVertex(T.label, "person", "name", "gin", "age", 88, "job", "drinker")
hal = tx.addVertex(T.label, "person", "name", "hal", "age", 9000, "job", "computer")
lilly = tx.addVertex(T.label, "person", "name", "lilly", "age", 43, "job", "flower")
magenta = tx.addVertex(T.label, "person", "name", "magenta", "age", 20, "job", "wrapper")
nina = tx.addVertex(T.label, "person", "name", "nina", "age", 38, "job", "director-CTU")
orin = tx.addVertex(T.label, "person", "name", "orin", "age", 25, "job", "orange")
peeves = tx.addVertex(T.label, "person", "name", "peeves", "age", 28, "job", "bulter")
quentin = tx.addVertex(T.label, "person", "name", "quentin", "age", 67, "job", "writer")
siobhan = tx.addVertex(T.label, "person", "name", "siobhan", "age", 55, "job", "smoker")
teegan = tx.addVertex(T.label, "person", "name", "teegan", "age", 26, "job", "maiden")
uknown = tx.addVertex(T.label, "person", "name", "unknown", "age", 8, "job", "pokemon")
yveltel = tx.addVertex(T.label, "person", "name", "yveltel", "age", 89, "job", "pokemon")
zante = tx.addVertex(T.label, "person", "name", "zante", "age", 123, "job", "island")
uk = tx.addVertex(T.label, "country", "name", "UK")
greece = tx.addVertex(T.label, "country", "name", "Greece")
staffs = tx.addVertex(T.label, "county", "name", "staffs", "population", 30000)
berks = tx.addVertex(T.label, "county", "name", "berks", "population", 45000)
norfolk = tx.addVertex(T.label, "county", "name", "norfolk", "population", 15000)
herts = tx.addVertex(T.label, "county", "name", "herts", "population", 43000)
hants = tx.addVertex(T.label, "county", "name", "hants", "population", 60000);
// edges
fish.addEdge("worksIn", staffs)
fish.addEdge("livesIn", uk)
fish.addEdge("knows", gin)
fish.addEdge("isRelated", gin).property("rela", "father")
fish.addEdge("knows", hal)
fish.addEdge("isRelated", teegan).property("rela", "mother")
fish.addEdge("knows", teegan)

tx.commit()

println "Finished"


