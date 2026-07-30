import sweph from 'sweph-wasm';

async function test() {
  const instance = new sweph();
  console.log("Instance:", Object.getOwnPropertyNames(Object.getPrototypeOf(instance)));
}

test();
