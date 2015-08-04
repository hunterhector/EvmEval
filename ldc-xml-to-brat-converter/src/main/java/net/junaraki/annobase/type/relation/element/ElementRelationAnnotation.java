package net.junaraki.annobase.type.relation.element;

import java.util.ArrayList;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.element.ElementAnnotation;
import net.junaraki.annobase.type.relation.RelationAnnotation;

/**
 * This class represents a general N-ary relation between element annotations.
 * 
 * @author Jun Araki
 *
 */
public abstract class ElementRelationAnnotation extends RelationAnnotation {

  private static final long serialVersionUID = 7590893032689339453L;

  /** Arguments that have this relation to each other */
  protected List<ElementAnnotation> args;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public ElementRelationAnnotation(AnnotationBase annBase) {
    super(annBase);
    args = new ArrayList<ElementAnnotation>();
  }

  @Override
  public List<ElementAnnotation> getArguments() {
    return args;
  }

  public void setArguments(List<ElementAnnotation> args) {
    this.args = args;
  }

  public void addArgument(ElementAnnotation argument) {
    args.add(argument);
  }

  @Override
  public int numArguments() {
    return args.size();
  }

}
