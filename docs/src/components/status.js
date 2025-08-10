// src/components/admonitions.js
import React from 'react';
import Admonition from '@theme/Admonition';

export function Info({children}) {
  return <Admonition type="info" title="Info">{children}</Admonition>;
}

export function Tip({children}) {
  return <Admonition type="tip" title="Tip">{children}</Admonition>;
}

export function Warning({children}) {
  return <Admonition type="warning" title="Warning">{children}</Admonition>;
}

export function Danger({children}) {
  return <Admonition type="danger" title="Danger">{children}</Admonition>;
}

export function Caution({children}) {
  return <Admonition type="caution" title="Caution">{children}</Admonition>;
}

export function Note({children}) {
  return <Admonition type="note" title="Note">{children}</Admonition>;
}
