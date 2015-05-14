package net.junaraki.annobase.util;

import java.util.Collection;

public class CollectionUtils {

  /**
   * Returns {@code true} if the given collection is null or empty.
   * 
   * @param col
   * @return
   */
  public static boolean isEmpty(final Collection<?> col) {
    return (col == null || col.isEmpty());
  }

}
