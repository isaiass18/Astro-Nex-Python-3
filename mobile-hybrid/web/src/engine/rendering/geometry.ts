/**
 * Converts degrees to radians.
 */
export function degreeToRad(deg: number): number {
  return (deg * Math.PI) / 180;
}

/**
 * Normalizes an angle to be between 0 and 360.
 */
export function normalizeDegree(deg: number): number {
  let normalized = deg % 360;
  if (normalized < 0) normalized += 360;
  return normalized;
}

/**
 * Calculates Cartesian coordinates for a point on a circle.
 * In astrological charts, the angle is drawn counter-clockwise.
 * 
 * @param cx Center X
 * @param cy Center Y
 * @param radius Radius from center
 * @param degree Astrological degree (0-360)
 * @param offsetDegree Visual offset (e.g., Ascendant degree) so it aligns to the left (180 deg on screen)
 */
export function polarToCartesian(
  cx: number,
  cy: number,
  radius: number,
  degree: number,
  offsetDegree: number = 0
) {
  // We want the offsetDegree to be on the left (180 screen degrees).
  // Formula: visual_angle = 180 - (degree - offsetDegree)
  const visualAngle = normalizeDegree(180 - degree + offsetDegree);
  const rad = degreeToRad(visualAngle);
  
  return {
    x: cx + radius * Math.cos(rad),
    y: cy + radius * Math.sin(rad) // Standard SVG mapping with positive sin
  };
}

/**
 * Calculates the shortest angular distance between two degrees.
 */
export function angularDistance(deg1: number, deg2: number): number {
  let diff = Math.abs(deg1 - deg2) % 360;
  return diff > 180 ? 360 - diff : diff;
}
