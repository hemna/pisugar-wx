# Research: Display 180° Rotation Setting

**Feature**: 003-display-180-rotation
**Date**: 2026-03-02

## Research Tasks

### 1. PIL Image Rotation Methods

**Decision**: Use `Image.Transpose` enum for rotation
**Rationale**: 
- `Image.Transpose.ROTATE_90`, `ROTATE_180`, `ROTATE_270` are efficient O(1) operations
- They don't require interpolation (just memory rearrangement)
- Already used in codebase for landscape rotation (`ROTATE_90`)

**Alternatives Considered**:
- `Image.rotate(angle)` - Uses interpolation, slower, can cause quality loss
- Manual pixel manipulation - Complex, slow, error-prone

### 2. Interaction with Existing Orientation Setting

**Decision**: Apply `display_rotation` after `orientation` rotation
**Rationale**:
- `orientation` determines how content is rendered (portrait vs landscape layout)
- `display_rotation` is a final transform for physical mounting
- Order: render → orientation rotation → display_rotation → show

**Current flow in app.py**:
```python
# Line 131-132: For landscape mode, rotate 90° before display
if orientation == "landscape" and Image is not None:
    image = image.transpose(Image.Transpose.ROTATE_90)
```

**New flow**:
```python
# Apply orientation-based rotation first (existing)
if orientation == "landscape":
    image = image.transpose(Image.Transpose.ROTATE_90)

# Apply display_rotation setting (new)
if display_rotation != 0:
    rotation_map = {
        90: Image.Transpose.ROTATE_90,
        180: Image.Transpose.ROTATE_180,
        270: Image.Transpose.ROTATE_270
    }
    image = image.transpose(rotation_map[display_rotation])
```

### 3. Configuration Value Validation

**Decision**: Validate rotation value, default to 0 if invalid
**Rationale**: Matches existing pattern for `orientation` validation in config.py

**Valid values**: 0, 90, 180, 270

### 4. Performance Impact

**Decision**: Negligible performance impact
**Rationale**:
- PIL Transpose operations are memory-efficient (pointer swaps, not pixel copies)
- 240x280 image is small (~200KB)
- Already doing one transpose for landscape mode
- Adding another transpose adds <1ms overhead

## Resolved Items

| Item | Resolution |
|------|------------|
| Rotation method | PIL Image.Transpose enum |
| Application order | After orientation rotation |
| Valid values | 0, 90, 180, 270 degrees |
| Default value | 0 (no rotation) |
| Validation | Log warning for invalid, default to 0 |
