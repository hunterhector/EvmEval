package net.junaraki.annobase.type.element;

import net.junaraki.annobase.AnnotationBase;

/**
 * This class represents an arbitrary text span without any substantive types.
 * 
 * @author Jun Araki
 */
public class TextSpan extends ElementAnnotation {

  private static final long serialVersionUID = -2340675842987975647L;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public TextSpan(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
  }

}
