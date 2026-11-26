"""Deterministic avoidance of a union of binary linear subspaces."""
def basis_of(vectors):
    basis={}
    for v in vectors:
        while v and v.bit_length()-1 in basis:
            v^=basis[v.bit_length()-1]
        if v:basis[v.bit_length()-1]=v
    return basis

def prefix_count(span,width,length,prefix):
    """Number of vectors in span with the specified high-bit prefix."""
    shift=width-length
    projected=basis_of(v>>shift for v in span.values())
    v=prefix
    while v and v.bit_length()-1 in projected:
        v^=projected[v.bit_length()-1]
    return 0 if v else 1<<(len(span)-len(projected))

def avoid_spans(spans,width):
    """Conditional counting; input bases independent and vectors in width bits."""
    spans=list(spans)
    if width<1 or sum(1<<len(s) for s in spans)>=1<<width:
        raise ValueError('union bound does not ensure a free label')
    prefix=0
    for length in range(1,width+1):
        a=prefix<<1
        count0=sum(prefix_count(s,width,length,a) for s in spans)
        count1=sum(prefix_count(s,width,length,a+1) for s in spans)
        prefix=a+int(count1<count0)
    if any(prefix_count(s,width,width,prefix) for s in spans):
        raise RuntimeError('conditional counting invariant failed')
    return prefix

def deterministic_codes(N):
    """Same width as the randomized local-code construction, no RNG."""
    n=len(N);delta=max(map(len,N),default=0)
    if not delta:return [],[0]*n
    width=delta+(delta-1).bit_length()+1
    if width>=n:return [1<<i for i in range(n)],[1<<i for i in range(n)]
    bases=[{} for _ in N];labels=[0]*n
    for j in range(n):
        v=avoid_spans([bases[i] for i in sorted(N[j])],width)
        labels[j]=v
        for i in sorted(N[j]):
            bases[i]=basis_of([*bases[i].values(),v])
    masks=[sum(1<<j for j in range(n) if labels[j]>>t&1) for t in range(width)]
    return masks,labels
