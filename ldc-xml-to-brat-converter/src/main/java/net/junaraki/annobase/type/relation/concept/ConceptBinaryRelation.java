package net.junaraki.annobase.type.relation.concept;

import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.Annotation;

/**
 * This class represents a binary relation between element annotations. It does not specify whether
 * the relation is directed or undirected.
 * 
 * @author Jun Araki
 */
public class ConceptBinaryRelation extends ConceptRelationAnnotation {

  private static final long serialVersionUID = 2618211145763426040L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public ConceptBinaryRelation(AnnotationBase annBase) {
    super(annBase);
  }

  @Override
  public String toString() {
    return String.format("%s [%s,%s] arg1:[%s] arg2:[%s]", getTypeName(), getId(),
            getRelationType(), getArg1(), getArg2());
  }

  public Annotation getArg1() {
    if (numArguments() < 1) {
      return null;
    }
    return args.get(0);
  }

  public void setArg1(Annotation arg1) {
    if (numArguments() == 0) {
      args.add(arg1);
    } else {
      args.set(0, arg1);
    }
  }

  public Annotation getArg2() {
    if (numArguments() < 2) {
      return null;
    }
    return args.get(1);
  }

  public void setArg2(Annotation arg2) {
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
  public void setArguments(List<Annotation> args) {
    if (args.size() > 2) {
      throw new IllegalArgumentException("A binary relation cannot hold more than two arguments.");
    }
    super.setArguments(args);
  }

  @Override
  public void addArgument(Annotation argument) {
    if (numArguments() == 2) {
      throw new IllegalArgumentException("A binary relation cannot hold more than two arguments.");
    }
    super.addArgument(argument);
  }

}
