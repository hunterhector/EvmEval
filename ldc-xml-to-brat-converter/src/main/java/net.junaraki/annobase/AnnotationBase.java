package net.junaraki.annobase;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import net.junaraki.annobase.type.Annotation;
import net.junaraki.annobase.type.concept.Entity;
import net.junaraki.annobase.type.concept.Event;
import net.junaraki.annobase.type.element.Chunk;
import net.junaraki.annobase.type.element.ConstituencyNode;
import net.junaraki.annobase.type.element.DependencyNode;
import net.junaraki.annobase.type.element.ElementAnnotation;
import net.junaraki.annobase.type.element.EntityMention;
import net.junaraki.annobase.type.element.EventMention;
import net.junaraki.annobase.type.element.Sentence;
import net.junaraki.annobase.type.element.Token;
import net.junaraki.annobase.type.graph.DependencyGraph;
import net.junaraki.annobase.type.relation.element.DependencyRelation;
import net.junaraki.annobase.type.relation.element.ElementRelationAnnotation;
import net.junaraki.annobase.type.relation.element.EventArgument;
import net.junaraki.annobase.type.relation.element.EventCoref;
import net.junaraki.annobase.type.relation.element.EventMentionRelation;
import net.junaraki.annobase.type.relation.element.SemanticRoleArgument;
import net.junaraki.annobase.util.CollectionUtils;
import net.junaraki.annobase.util.SourceDocument;

/**
 * An annotation base is more like an annotation manager. This class manages annotations for a
 * srcDocument with multiple annotation collections.
 * 
 * @author Jun Araki
 */
public class AnnotationBase implements Serializable {

  private static final long serialVersionUID = -6102329989032743291L;

  /** A document where this annotation base manages annotations */
  protected final SourceDocument srcDoc;

  /**
   * A data structure that stores annotations in this annotation base, mapping from a type name to a
   * list of annotations of that type.
   */
  protected Map<Class<?>, List<Annotation>> annMap;

  /** Lazily initialized, cached hashCode */
  private volatile int hashCode;

  /**
   * Public constructor.
   * 
   * @param text
   */
  public AnnotationBase(String text) {
    srcDoc = new SourceDocument(text);
    initialize();
  }

  /**
   * Public constructor.
   * 
   * @param text
   * @param docId
   */
  public AnnotationBase(String text, String docId) {
    srcDoc = new SourceDocument(text, docId);
    initialize();
  }

  /**
   * Initializes this annotation base.
   */
  protected void initialize() {
    annMap = new HashMap<Class<?>, List<Annotation>>();
  }

  @Override
  public String toString() {
    StringBuilder buf = new StringBuilder();
    for (Class<?> clazz : annMap.keySet()) {
      buf.append(clazz + ": " + annMap.get(clazz));
      buf.append(System.lineSeparator());
    }
    return buf.toString();
  }

  @Override
  public boolean equals(Object obj) {
    if (obj == this) {
      return true;
    }
    if (!(obj instanceof AnnotationBase)) {
      return false;
    }

    AnnotationBase that = (AnnotationBase) obj;
    if (!srcDoc.equals(that.getSourceDocument())) {
      return false;
    }
    if (!annMap.equals(that.getAnnotationMap())) {
      return false;
    }

    return true;
  }

  @Override
  public int hashCode() {
    int result = hashCode;
    if (result == 0) {
      result = 17;
      result = 31 * result + srcDoc.hashCode();
      hashCode = result;
    }

    return result;
  }

  public SourceDocument getSourceDocument() {
    return srcDoc;
  }

  public String getDocumentText() {
    return srcDoc.getText();
  }

  public Map<Class<?>, List<Annotation>> getAnnotationMap() {
    return annMap;
  }

  /**
   * Returns true if this annotation base has any annotations of the given type.
   * 
   * @param clazz
   * @return
   */
  public <T extends Annotation> boolean hasAnnotation(Class<T> clazz) {
    return annMap.containsKey(clazz);
  }

  /**
   * Returns true if this annotation base has annotation of the given type which has the same span
   * as the given annotation.
   * 
   * @param clazz
   * @param comparedAnn
   * @return
   */
  public <T extends ElementAnnotation> boolean hasAnnotationWithSameSpanAs(Class<T> clazz,
          ElementAnnotation comparedAnn) {
    for (T ann : getAnnotations(clazz)) {
      if (ann.hasSameSpan(comparedAnn)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Returns true if this annotation base has annotation of the given type which has the same span
   * as the given annotation.
   * 
   * @param clazz
   * @param begin
   * @param end
   * @return
   */
  public <T extends ElementAnnotation> boolean hasAnnotationWithSameSpanAs(Class<T> clazz,
          int begin, int end) {
    for (T ann : getAnnotations(clazz)) {
      if (ann.getBegin() == begin && ann.getEnd() == end) {
        return true;
      }
    }

    return false;
  }

  /**
   * Returns a list of annotations of the given type in this annotation base.
   * 
   * @param clazz
   * @return
   */
  @SuppressWarnings({ "cast", "unchecked" })
  public <T extends Annotation> List<T> getAnnotations(Class<T> clazz) {
    if (!hasAnnotation(clazz)) {
      return new ArrayList<T>();
    }

    return (List<T>) annMap.get(clazz);
  }

  /**
   * Returns a list of annotations of the given type in this annotation base, covering the given
   * element annotation.
   * 
   * @param clazz
   * @param coveredAnn
   * @return
   */
  public <T extends ElementAnnotation> List<T> getAnnotationsCovering(Class<T> clazz,
          ElementAnnotation coveredAnn) {
    List<T> annList = new ArrayList<T>();
    for (T ann : getAnnotations(clazz)) {
      if (ann.cover(coveredAnn)) {
        annList.add(ann);
      }
    }

    return annList;
  }

  /**
   * Returns a list of annotations of the given type in this annotation base, covered by the given
   * element annotation.
   * 
   * @param clazz
   * @param coveringAnn
   * @return
   */
  public <T extends ElementAnnotation> List<T> getAnnotationsCoveredBy(Class<T> clazz,
          ElementAnnotation coveringAnn) {
    List<T> annList = new ArrayList<T>();
    for (T ann : getAnnotations(clazz)) {
      if (ann.coveredBy(coveringAnn)) {
        annList.add(ann);
      }
    }

    return annList;
  }

  /**
   * Returns a list of annotations of the given type in this annotation base, covered by the text
   * span specified by the given offsets.
   * 
   * @param clazz
   * @param begin
   * @param end
   * @return
   */
  public <T extends ElementAnnotation> List<T> getAnnotationsCoveredBy(Class<T> clazz, int begin,
          int end) {
    List<T> annList = new ArrayList<T>();
    for (T ann : getAnnotations(clazz)) {
      if (ann.coveredBy(begin, end)) {
        annList.add(ann);
      }
    }

    return annList;
  }

  /**
   * Returns a list of annotations of the given type in this annotation base, which have the same
   * span as the given element annotation.
   * 
   * @param clazz
   * @param comparedAnn
   * @return
   */
  public <T extends ElementAnnotation> List<T> getAnnotationsWithSameSpanAs(Class<T> clazz,
          ElementAnnotation comparedAnn) {
    List<T> annList = new ArrayList<T>();
    for (T ann : getAnnotations(clazz)) {
      if (ann.hasSameSpan(comparedAnn)) {
        annList.add(ann);
      }
    }

    return annList;
  }

  /**
   * Returns a list of annotations of the given type in this annotation base, which have the given
   * offset.
   * 
   * @param clazz
   * @param begin
   * @param end
   * @return
   */
  public <T extends ElementAnnotation> List<T> getAnnotationsWithSameSpanAs(Class<T> clazz,
          int begin, int end) {
    List<T> annList = new ArrayList<T>();
    for (T ann : getAnnotations(clazz)) {
      if (ann.getBegin() == begin && ann.getEnd() == end) {
        annList.add(ann);
      }
    }

    return annList;
  }

  /**
   * Returns a list of relation annotations of the given type in this annotation base, each of whose
   * arguments is covered by the given element annotation.
   * 
   * @param clazz
   * @param coveringAnn
   * @return
   */
  public <T extends ElementRelationAnnotation> List<T> getRelationAnnotationsCoveredBy(
          Class<T> clazz, ElementAnnotation coveringAnn) {
    List<T> annList = new ArrayList<T>();
    for (T ann : getAnnotations(clazz)) {
      boolean covered = true;
      for (ElementAnnotation e : ann.getArguments()) {
        if (!e.coveredBy(coveringAnn)) {
          covered = false;
          break;
        }
      }
      if (covered) {
        annList.add(ann);
      }
    }

    return annList;
  }

  /**
   * Returns an annotation of the given type. This is convenient if you are sure that there is only
   * one annotation instance in this annotation collection.
   * 
   * @param clazz
   * @return
   */
  public <T extends Annotation> T getAnnotation(Class<T> clazz) {
    List<T> anns = getAnnotations(clazz);
    if (CollectionUtils.isEmpty(anns)) {
      return null;
    } else {
      return anns.get(0);
    }
  }

  /**
   * Adds the given annotation to this annotation base.
   * 
   * @param ann
   */
  public <T extends Annotation> void addAnnotation(T ann) {
    if (!ann.getAnnotationBase().equals(this)) {
      throw new RuntimeException("Invalid annotation base found.");
    }

    Class<?> clazz = ann.getClass();
    if (annMap.containsKey(clazz)) {
      annMap.get(clazz).add(ann);
    } else {
      List<Annotation> anns = new ArrayList<Annotation>();
      anns.add(ann);
      annMap.put(clazz, anns);
    }
  }

  /**
   * Adds the given annotations to this annotation base.
   * 
   * @param annList
   */
  public <T extends Annotation> void addAnnotations(List<T> annList) {
    if (CollectionUtils.isEmpty(annList)) {
      return;
    }

    for (T ann : annList) {
      addAnnotation(ann);
    }
  }

  public <T extends Annotation> void removeAnnotation(T ann) {
    for (Class<?> clazz : annMap.keySet()) {
      annMap.get(clazz).remove(ann);
    }
  }

  public <T extends Annotation> void removeAnnotations(Class<T> clazz) {
    if (hasAnnotation(clazz)) {
      annMap.remove(clazz);
    }
  }

  public <T extends Annotation> void setAnnotations(List<T> annList) {
    if (CollectionUtils.isEmpty(annList)) {
      return;
    }

    removeAnnotations(annList.get(0).getClass());
    addAnnotations(annList);
  }

  /**
   * Returns the total number of annotations in this annotation base.
   * 
   * @return
   */
  public int numAnnotations() {
    return annMap.size();
  }

  /**
   * Returns the number of annotations of the given type in this document.
   * 
   * @param clazz
   * @return
   */
  public <T extends Annotation> int numAnnotations(Class<T> clazz) {
    if (!hasAnnotation(clazz)) {
      return 0;
    }
    return annMap.get(clazz).size();
  }

  public List<Token> getTokens() {
    return getAnnotations(Token.class);
  }

  public List<Sentence> getSentences() {
    return getAnnotations(Sentence.class);
  }

  public List<Chunk> getChunks() {
    return getAnnotations(Chunk.class);
  }

  public List<ConstituencyNode> getConstituencyNodes() {
    return getAnnotations(ConstituencyNode.class);
  }

  public List<DependencyNode> getDependencyNodes() {
    return getAnnotations(DependencyNode.class);
  }

  public List<DependencyRelation> getDependencyRelations() {
    return getAnnotations(DependencyRelation.class);
  }

  public List<DependencyGraph> getDependencyGraph() {
    return getAnnotations(DependencyGraph.class);
  }

  public List<SemanticRoleArgument> getSemanticRoleRelations() {
    return getAnnotations(SemanticRoleArgument.class);
  }

  public List<Entity> getEntities() {
    return getAnnotations(Entity.class);
  }

  public List<EntityMention> getEntityMentions() {
    return getAnnotations(EntityMention.class);
  }

  public List<Event> getEvents() {
    return getAnnotations(Event.class);
  }

  /**
   * Sets events from event coreference annotation.
   */
  public void setEventsFromEventCoref() {
    List<Set<EventMention>> clusters = new ArrayList<Set<EventMention>>();
    for (EventCoref coref : getEventCorefs()) {
      EventMention evm1 = coref.getFrom();
      EventMention evm2 = coref.getTo();

      Set<EventMention> cluster1 = findCluster(clusters, evm1);
      Set<EventMention> cluster2 = findCluster(clusters, evm2);

      if (cluster1 == null && cluster2 == null) {
        // Create a new cluster
        Set<EventMention> cluster = new HashSet<EventMention>();
        cluster.add(evm1);
        cluster.add(evm2);
        clusters.add(cluster);

      } else if (cluster1 != null && cluster2 == null) {
        cluster1.add(evm2);

      } else if (cluster1 == null && cluster2 != null) {
        cluster2.add(evm1);

      } else if (cluster1 != null && cluster2 != null) {
        if (cluster1.equals(cluster2)) {
          // Skip because they are already in the same cluster
          continue;
        } else {
          // Merge the two clusters
          cluster1.addAll(cluster2);
          clusters.remove(cluster2);
        }
      }
    }

    // First, annotate coreferential event mentions.
    for (Set<EventMention> cluster : clusters) {
      Event event = new Event(this);
      event.setEventMentions(new ArrayList<EventMention>(cluster));
      event.addToBase();

      for (EventMention evm : cluster) {
        evm.setEvent(event);
      }
    }

    // Second, annotate singleton event mentions.
    for (EventMention evm : getEventMentions()) {
      if (evm.getEvent() != null) {
        continue;
      }

      Event event = new Event(this);
      event.setEventMentions(Arrays.asList(evm));
      event.addToBase();

      evm.setEvent(event);
    }
  }

  /**
   * Returns an cluster which the given event mention belongs to. If there is no cluster, returns
   * null.
   * 
   * @param clusters
   * @param evm
   * @return
   */
  private Set<EventMention> findCluster(List<Set<EventMention>> clusters, EventMention evm) {
    for (Set<EventMention> cluster : clusters) {
      if (cluster.contains(evm)) {
        return cluster;
      }
    }

    return null;
  }

  public List<EventMention> getEventMentions() {
    return getAnnotations(EventMention.class);
  }

  public List<EventArgument> getEventArguments() {
    return getAnnotations(EventArgument.class);
  }

  public List<EventCoref> getEventCorefs() {
    return getAnnotations(EventCoref.class);
  }

  public List<net.junaraki.annobase.type.relation.concept.Subevent> getConceptBasedSubevents() {
    return getAnnotations(net.junaraki.annobase.type.relation.concept.Subevent.class);
  }

  public List<net.junaraki.annobase.type.relation.element.Subevent> getMentionBasedSubevents() {
    return getAnnotations(net.junaraki.annobase.type.relation.element.Subevent.class);
  }

  public List<EventMentionRelation> getEventMentionRelations() {
    return getAnnotations(EventMentionRelation.class);
  }

}
