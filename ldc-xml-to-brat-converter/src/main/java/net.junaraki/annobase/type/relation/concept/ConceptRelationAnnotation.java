package net.junaraki.annobase.type.relation.concept;

import java.util.ArrayList;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.Annotation;
import net.junaraki.annobase.type.relation.RelationAnnotation;

/**
 * This class represents a general N-ary relation between concept annotations.
 * 
 * @author Jun Araki
 *
 */
public abstract class ConceptRelationAnnotation extends RelationAnnotation {

  private static final long serialVersionUID = -7489550381569411806L;

  /** Arguments that have this relation to each other */
  protected List<Annotation> args;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public ConceptRelationAnnotation(AnnotationBase annBase) {
    super(annBase);
    args = new ArrayList<Annotation>();
  }

  @Override
  public List<Annotation> getArguments() {
    return args;
  }

  public void setArguments(List<Annotation> args) {
    this.args = args;
  }

  public void addArgument(Annotation argument) {
    args.add(argument);
  }

  @Override
  public int numArguments() {
    return args.size();
  }

}
