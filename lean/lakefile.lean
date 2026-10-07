import Lake
open Lake DSL

package qnn_core where
  leanOptions := #[
    ⟨`pp.unicode.fun, true⟩ -- pretty-printer
  ]

require leanprover / lean4

@[default_target]
lean_lib QNNCore where
  roots := #[`QNNCore]
