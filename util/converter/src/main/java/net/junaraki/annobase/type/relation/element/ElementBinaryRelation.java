package net.junaraki.annobase.type.relation.element;

import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.element.ElementAnnotation;

/**
 * This class represents a binary relation between element annotations. It does not specify whether
 * the relation is directed or undirected.
 * 
 * @author Jun Araki
 */
public class ElementBinaryRelation extends ElementRelationAnnotation {

  private static final long serialVersionUID = -7770046340863201781L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public ElementBinaryRelation(AnnotationBase annBase) {
    super(annBase);
  }

  @Override
  public String toString() {
    return String.format("%s [%s,%s] arg1:[%s] arg2:[%s]", getTypeName(), getId(),
            getRelationType(), getArg1(), getArg2());
  }

  public ElementAnnotation getArg1() {
    if (numArguments() < 1) {
      return null;
    }
    return args.get(0);
  }

  public void setArg1(ElementAnnotation arg1) {
    if (numArguments() == 0) {
      args.add(arg1);
    } else {
      args.set(0, arg1);
    }
  }

  public ElementAnnotation getArg2() {
    if (numArguments() < 2) {
      return null;
    }
    return args.get(1);
  }

  public void setArg2(ElementAnnotation arg2) {
    int numArguments = numArguments();
    if (numArguments < 2) {
      if (numArguments == 0) {
        args.add(null);
      }
      args.add(arg2);
    } else {
      args.set(1, arg2);
    }
  }

  @Override
  public void setArguments(List<ElementAnnotation> args) {
    if (args.size() > 2) {
      throw new IllegalArgumentException("A binary relation cannot hold more than two arguments.");
    }
    super.setArguments(args);
  }

  @Override
  public void addArgument(ElementAnnotation argument) {
    if (numArguments() == 2) {
      throw new IllegalArgumentException("A binary relation cannot hold more than two arguments.");
    }
    super.addArgument(argument);
  }

}
