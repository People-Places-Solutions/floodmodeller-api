from lxml import etree


def copy_tree_with_new_namespace(original_root, root_ns_map: dict, root_attrib_map: dict):
    """
    Copy an lxml.etree tree with a new root and all tags in a new namespace.
    Avoids 'ns0' by explicitly defining the namespace mapping.
    """

    default_namespace = root_ns_map[None]

    # Create new root element
    new_root = etree.Element(
        f"{{{default_namespace}}}{etree.QName(original_root).localname}",
        nsmap=root_ns_map,
        attrib={k: v for k, v in original_root.attrib.items()})

    for k1, _ in new_root.attrib.items():
        for k2, v2 in root_attrib_map.items():            
            k1_key = etree.QName(k1).localname
            k2_key = etree.QName(k2).localname
            if k1_key == k2_key:
                new_root.attrib[k1] = v2
                break

    def recursive_copy(src_elem, dst_parent):
        """Recursively copy elements into the new namespace."""
        for child in src_elem:
            if isinstance(child, etree._Comment):
                dst_parent.append(etree.Comment(child.text))
            elif isinstance(child.tag, str):
                # Create new element in the new namespace
                new_child = etree.SubElement(
                    dst_parent,
                    f"{{{default_namespace}}}{etree.QName(child).localname}",
                    attrib={k: v for k, v in child.attrib.items()}
                )
                # Copy text and tail
                new_child.text = child.text
                new_child.tail = child.tail
                # Recurse into children
                recursive_copy(child, new_child)

    # Copy children from original root into new root
    recursive_copy(original_root, new_root)

    return new_root
