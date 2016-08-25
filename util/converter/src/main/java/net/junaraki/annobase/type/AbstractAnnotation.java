package net.junaraki.annobase.type;

import java.io.Serializable;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.util.SourceDocument;

/**
 * This class provides a skeletal implementation of the Annotation interface.
 * 
 * @author Jun Araki
 */
public abstract class AbstractAnnotation implements Annotation, Serializable {

  private static final long serialVersionUID = -1984225230534457249L;

  /** A document where this annotation is annotated */
  protected final AnnotationBase annBase;

  /** Optional field: ID of this annotation, implemented as an integer */
  protected int id;

  /** Optional field: annotator ID for this annotation */
  protected String annotatorId;

  /** Lazily initialized, cached hashCode */
  protected volatile int hashCode;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public AbstractAnnotation(AnnotationBase annBase) {
    this.annBase = annBase;
  }

  @Override
  public boolean equals(Object obj) {
    if (obj == this) {
      return true;
    }
    if (!(obj instanceof AbstractAnnotation)) {
      return false;
    }

    AbstractAnnotation that = (AbstractAnnotation) obj;
    // It is sufficient to check a source document only for the annotation base.
    if (!annBase.getSourceDocument().equals(that.getAnnotationBase().getSourceDocument())) {
      return false;
    }

    if (!getTypeName().equals(that.getTypeName())) {
      return false;
    }

    // if (id != that.getId()) {
    // return false;
    // }

    return true;
  }

  @Override
  public int hashCode() {
    int result = hashCode;
    if (result == 0) {
      result = 17;
      result = 31 * result + getAnnotationBase().hashCode();
      result = 31 * result + getTypeName().hashCode();
      // result = 31 * result + id;
      hashCode = result;
    }

    return result;
  }

  @Override
  public AnnotationBase getAnnotationBase() {
    return annBase;
  }

  public SourceDocument getSourceDocument() {
    return annBase.getSourceDocument();
  }

  @Override
  public String getTypeName() {
    return getClass().getSimpleName();
    //return typeName;
  }

  /**
   * Adds this annotation to an associated annotation base. The association of the annotation with
   * an annotation base is done in creating the annotation.
   */
  @Override
  public void addToBase() {
    annBase.addAnnotation(this);
  }

  @Override
  public void removeFromBase() {
    annBase.removeAnnotation(this);
  }

  public int getId() {
    return id;
  }

  public void setId(int id) {
    this.id = id;
  }

  public String getAnnotatorId() {
    return annotatorId;
  }

  public void setAnnotatorId(String annotatorId) {
    this.annotatorId = annotatorId;
  }

}
