package net.junaraki.annobase.type.relation.concept;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.Annotation;

/**
 * This class represents a directed binary relation between element annotations.
 * 
 * @author Jun Araki
 */
public class ConceptDirectedBinaryRelation extends ConceptBinaryRelation {

  private static final long serialVersionUID = 2179982786649015997L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public ConceptDirectedBinaryRelation(AnnotationBase annBase) {
    super(annBase);
  }

  @Override
  public String toString() {
    return String.format("%s [%s,%s] from:[%s] to:[%s]", getTypeName(), getId(), getRelationType(),
            getFrom(), getTo());
  }

  public Annotation getFrom() {
    return getArg1();
  }

  public void setFrom(Annotation from) {
    setArg1(from);
  }

  public Annotation getTo() {
    return getArg2();
  }

  public void setTo(Annotation to) {
    setArg2(to);
  }

}
