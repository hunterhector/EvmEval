package net.junaraki.annobase.type;

import net.junaraki.annobase.AnnotationBase;

/**
 * An interface for annotation. An annotation represents either a particular span of text (i.e., an
 * elemental annotation) or an abstract object with respect to some elemental annotations. It has
 * access to a document that it belongs to.
 * 
 * @author Jun Araki
 */
public interface Annotation {

  /**
   * Returns the type name of this annotation.
   * 
   * @return
   */
  public String getTypeName();

  /**
   * Returns the annotation base which this annotation belongs to.
   * 
   * @return
   */
  public AnnotationBase getAnnotationBase();

  /**
   * Adds this annotation to an associated annotation base. The association of the annotation with
   * an annotation base is done in creating the annotation.
   */
  public void addToBase();

  /**
   * Removes this annotation from an associated annotation base.
   */
  public void removeFromBase();

}
