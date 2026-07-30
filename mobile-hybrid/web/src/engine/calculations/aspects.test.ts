import { describe, it, expect } from 'vitest';
import { calculateAspects, calculateDrawAspects } from './aspects';
import { EngineSettings } from './types';
import fs from 'fs';
import path from 'path';

describe('Aspects Calculations', () => {
  it('should match Python Golden Fixture exactly', () => {
    // Load config and outputs
    const configPath = path.resolve(__dirname, '../../../../tests/golden/config_orbs.json');
    const aspectsPath = path.resolve(__dirname, '../../../../tests/golden/aspects_output.json');
    const natalPath = path.resolve(__dirname, '../../../../tests/golden/natal_output.json');

    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const goldenAspects = JSON.parse(fs.readFileSync(aspectsPath, 'utf8'));
    const natal = JSON.parse(fs.readFileSync(natalPath, 'utf8'));

    const settings: EngineSettings = {
      orbs: config.orbs,
      peorbs: config.peorbs
    };

    const planets = natal.planets.map((p: any) => p.longitude);
    
    // We expect Node to be at index 10 (True Node/Mean Node, depending on what Python output).
    // In Astro-Nex, `planets` array has 11 elements (Sun to Pluto, plus Node at index 10).
    const radixAspects = calculateAspects(planets, settings);
    const drawAspects = calculateDrawAspects(planets, settings);

    // Compare Aspects Radix
    expect(radixAspects.length).toBe(goldenAspects.aspects_radix.length);
    for (let i = 0; i < radixAspects.length; i++) {
      const a = radixAspects[i];
      const g = goldenAspects.aspects_radix[i];
      expect(a.p1).toBe(g.p1);
      expect(a.p2).toBe(g.p2);
      expect(a.a).toBe(g.a);
      expect(a.gw).toBe(g.gw);
      expect(a.f1).toBeCloseTo(g.f1, 5);
      expect(a.f2).toBeCloseTo(g.f2, 5);
    }

    // Compare Draw Aspects
    expect(drawAspects.length).toBe(goldenAspects.calc_aspects.length);
    for (let i = 0; i < drawAspects.length; i++) {
      const a = drawAspects[i];
      const g = goldenAspects.calc_aspects[i];
      expect(a.p1).toBe(g.p1);
      expect(a.p2).toBe(g.p2);
      expect(a.a).toBe(g.a);
      expect(a.f1).toBeCloseTo(g.f1, 5);
      expect(a.f2).toBeCloseTo(g.f2, 5);
    }
  });
});
