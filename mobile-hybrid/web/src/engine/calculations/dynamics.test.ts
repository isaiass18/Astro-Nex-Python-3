import { describe, it, expect } from 'vitest';
import { calculateSignDyn, calculateHouseDyn } from './dynamics';
import fs from 'fs';
import path from 'path';

describe('Dynamics Calculations', () => {
  it('should match Python Golden Fixture exactly', () => {
    // Load config and outputs
    const dynamicsPath = path.resolve(__dirname, '../../../../tests/golden/dynamics_output.json');
    const natalPath = path.resolve(__dirname, '../../../../tests/golden/natal_output.json');

    const goldenDynamics = JSON.parse(fs.readFileSync(dynamicsPath, 'utf8'));
    const natal = JSON.parse(fs.readFileSync(natalPath, 'utf8'));

    const planets = natal.planets.map((p: any) => p.longitude);
    const houses = natal.houses;

    const signDyn = calculateSignDyn(planets, houses);
    const houseDyn = calculateHouseDyn(planets, houses);

    // Assert Sign Dyn
    expect(signDyn.elem.fire).toBe(goldenDynamics.signdyn.elem.fire);
    expect(signDyn.elem.earth).toBe(goldenDynamics.signdyn.elem.earth);
    expect(signDyn.elem.air).toBe(goldenDynamics.signdyn.elem.air);
    expect(signDyn.elem.water).toBe(goldenDynamics.signdyn.elem.water);
    expect(signDyn.cross.card).toBe(goldenDynamics.signdyn.cross.card);
    expect(signDyn.cross.fix).toBe(goldenDynamics.signdyn.cross.fix);
    expect(signDyn.cross.mut).toBe(goldenDynamics.signdyn.cross.mut);

    // Assert House Dyn
    expect(houseDyn.elem.fire).toBe(goldenDynamics.housedyn.elem.fire);
    expect(houseDyn.elem.earth).toBe(goldenDynamics.housedyn.elem.earth);
    expect(houseDyn.elem.air).toBe(goldenDynamics.housedyn.elem.air);
    expect(houseDyn.elem.water).toBe(goldenDynamics.housedyn.elem.water);
    expect(houseDyn.cross.card).toBe(goldenDynamics.housedyn.cross.card);
    expect(houseDyn.cross.fix).toBe(goldenDynamics.housedyn.cross.fix);
    expect(houseDyn.cross.mut).toBe(goldenDynamics.housedyn.cross.mut);
  });
});
