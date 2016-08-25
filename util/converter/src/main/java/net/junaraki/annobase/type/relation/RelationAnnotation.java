package net.junaraki.annobase.type.relation;

import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.AbstractAnnotation;

/**
 * This class represents a general N-ary relation between annotations.
 * 
 * @author Jun Araki
 *
 */
public abstract class RelationAnnotation extends AbstractAnnotation {

  private static final long serialVersionUID = -5434453547709520417L;

  /** A relation type for this relation */
  protected String relationType;

  /** Lazily initialized, cached hashCode */
  protected volatile int hashCode;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public RelationAnnotation(AnnotationBase annBase) {
    super(annBase);
  }

  @Override
  public boolean equals(Object obj) {
    if (obj == this) {
      return true;
    }
    // Expect a super class to compare source documents and type names.
    if (!super.equals(obj)) {
      return false;
    }
    if (!(obj instanceof RelationAnnotation)) {
      return false;
    }

    RelationAnnotation that = (RelationAnnotation) obj;
    if (!getArguments().equals(that.getArguments())) {
      return false;
    }

    String thatRelationType = that.getRelationType();
    if (relationType == null) {
      if (thatRelationType != null) {
        return false;
      }
    } else {
      if (!relationType.equals(thatRelationType)) {
        return false;
      }
    }

    return true;
  }

  @Override
  public int hashCode() {
    int result = hashCode;
    if (result == 0) {
      result = 17;
      result = 31 * result + super.hashCode();
      result = 31 * result + getArguments().hashCode();
      if (relationType != null) {
        result = 31 * result + relationType.hashCode();
      }
      hashCode = result;
    }

    return result;
  }

  public abstract List<?> getArguments();

  public abstract int numArguments();

  public String getRelationType() {
    return relationType;
  }

  public void setRelationType(String relationType) {
    this.relationType = relationType;
  }

}
