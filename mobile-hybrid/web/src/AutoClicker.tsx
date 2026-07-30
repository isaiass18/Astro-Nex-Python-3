import { useEffect } from 'react';

export const AutoClicker = () => {
    useEffect(() => {
        setTimeout(() => {
            const buttons = document.querySelectorAll('*');
            for (let b of buttons) {
                if (b.textContent === 'Calcular Carta') {
                    (b as HTMLElement).click();
                    break;
                }
            }
        }, 1000);
    }, []);
    return null;
};
