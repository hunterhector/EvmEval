package net.junaraki.annobase.type.relation.element;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.element.ElementAnnotation;

/**
 * This class represents a directed binary relation between element annotations.
 * 
 * @author Jun Araki
 */
public class ElementDirectedBinaryRelation extends ElementBinaryRelation implements
        Comparable<ElementDirectedBinaryRelation> {

  private static final long serialVersionUID = -3449711139833297415L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public ElementDirectedBinaryRelation(AnnotationBase annBase) {
    super(annBase);
  }

  @Override
  public String toString() {
    return String.format("%s [%s,%s] from:[%s] to:[%s]", getTypeName(), getId(), getRelationType(),
            getFrom(), getTo());
  }

  @Override
  public int compareTo(ElementDirectedBinaryRelation that) {
    int compareFrom = getFrom().compareTo(that.getFrom());
    if (compareFrom < 0) {
      return -1;
    } else if (compareFrom > 0) {
      return 1;
    } else {
      int compareTo = getTo().compareTo(that.getTo());
      if (compareTo < 0) {
        return -1;
      } else if (compareTo > 0) {
        return 1;
      } else {
        return 0;
      }
    }
  }

  public ElementAnnotation getFrom() {
    return getArg1();
  }

  public void setFrom(ElementAnnotation from) {
    setArg1(from);
  }

  public ElementAnnotation getTo() {
    return getArg2();
  }

  public void setTo(ElementAnnotation to) {
    setArg2(to);
  }

}
