package net.junaraki.annobase.type.element;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.graph.DependencyGraph;
import net.junaraki.annobase.type.relation.element.DependencyRelation;

/**
 * A sentence annotation.
 * 
 * @author Jun Araki
 */
public class Sentence extends TokenBasedTextSpan {

  private static final long serialVersionUID = -4873614722828332924L;

  protected Document doc;

  protected DependencyGraph depGraph;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public Sentence(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
    doc = null;
    depGraph = null;
  }

  /**
   * Returns true if this sentence is the first one in the document which it belongs to.
   * 
   * @return
   */
  public boolean isFirstSentence() {
    if (doc == null) {
      return false;
    }
    if (doc.numSentences() == 0) {
      return false;
    }

    if (doc.getSentenceAt(0).equals(this)) {
      return true;
    }

    return false;
  }

  /**
   * Returns true if this sentence is the last one in the document which it belongs to.
   * 
   * @return
   */
  public boolean isLastSentence() {
    if (doc == null) {
      return false;
    }
    if (doc.numSentences() == 0) {
      return false;
    }

    if (doc.getSentenceAt(doc.numSentences() - 1).equals(this)) {
      return true;
    }

    return false;
  }

  public Document getDocument() {
    return doc;
  }

  public void setDocument(Document doc) {
    this.doc = doc;
  }

  /**
   * Constructs a dependency graph in this sentence using dependency annotation.
   */
  public void constructDependencyGraph() {
    DependencyGraph depGraph = new DependencyGraph(annBase);

    for (DependencyNode depNode : annBase.getAnnotationsCoveredBy(DependencyNode.class, this)) {
      if (depNode.isRoot()) {
        depGraph.setRoot(depNode);
      }
      for (DependencyRelation headRel : depNode.getHeadRelations()) {
        depGraph.addEdge(headRel, depNode, headRel.getHead());
      }
      for (DependencyRelation childRel : depNode.getChildRelations()) {
        depGraph.addEdge(childRel, depNode, childRel.getChild());
      }
    }

    this.depGraph = depGraph;
  }

  public DependencyGraph getDependencyGraph() {
    if (depGraph == null) {
      constructDependencyGraph();
    }
    return depGraph;
  }

}
