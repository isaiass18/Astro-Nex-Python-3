import React, { useRef, useState } from 'react';

export const KonstaAppWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <main className="offline-app">{children}</main>
);

export const Form: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="offline-form">{children}</div>
);

export const Section: React.FC<{ title?: string; children: React.ReactNode }> = ({ title, children }) => (
  <section className="offline-section">
    {title && <h2 className="offline-section-title">{title}</h2>}
    <div className="offline-card">{children}</div>
  </section>
);

export const FormRow: React.FC<{
  children: React.ReactNode;
  onClick?: () => void;
  style?: React.CSSProperties;
}> = ({ children, onClick, style }) => (
  <div className={`offline-row${onClick ? ' is-clickable' : ''}`} onClick={onClick} style={style}>
    {children}
  </div>
);

export const LabeledContent: React.FC<{ label: string; value: string | React.ReactNode }> = ({ label, value }) => (
  <div className="offline-row offline-labeled-content">
    <span>{label}</span>
    <span className="offline-value">{value}</span>
  </div>
);

export const TextField: React.FC<{
  placeholder: string;
  value: string;
  onChange: (val: string) => void;
  onEnter?: () => void;
}> = ({ placeholder, value, onChange, onEnter }) => (
  <div className="offline-row">
    <input className="offline-input" type="text" placeholder={placeholder} value={value}
      onChange={(event) => onChange(event.target.value)}
      onKeyDown={(event) => event.key === 'Enter' && onEnter?.()} />
  </div>
);

export const Toggle: React.FC<{ label: string; checked: boolean; onChange: (val: boolean) => void }> = ({ label, checked, onChange }) => (
  <label className="offline-row offline-toggle-row">
    <span>{label}</span>
    <input className="offline-toggle" type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
  </label>
);

export const Button: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement>> = ({ className = '', children, ...props }) => (
  <button className={`offline-primary-button ${className}`.trim()} {...props}>{children}</button>
);

export const NavigationBar: React.FC<{
  title: string;
  menuOptions: { id: string; label: string; icon: string }[];
  onSelectMenu: (id: string) => void;
  selectedMenu: string;
}> = ({ title, menuOptions, onSelectMenu }) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  return (
    <header className="offline-header">
      <h1>{title}</h1>
      <div className="offline-menu-wrap" ref={menuRef}>
        <button className="offline-menu-button" aria-label="Abrir menú" onClick={() => setIsOpen((open) => !open)}>
          <svg width="31" height="31" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <circle cx="12" cy="12" r="10.5" />
            <path d="M7 9h10M9 12h6M11 15h2" />
          </svg>
        </button>
        {isOpen && <nav className="offline-menu">
          {menuOptions.map((option) => <button key={option.id} onClick={() => { onSelectMenu(option.id); setIsOpen(false); }}>{option.label}</button>)}
        </nav>}
      </div>
    </header>
  );
};

export const SegmentedControl: React.FC<{ options: { id: string; label: string }[]; selected: string; onChange: (id: string) => void }> = ({ options, selected, onChange }) => (
  <div className="offline-segmented">
    {options.map((option) => <button key={option.id} className={selected === option.id ? 'active' : ''} onClick={() => onChange(option.id)}>{option.label}</button>)}
  </div>
);

export const DisclosureGroup: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => {
  const [isOpen, setIsOpen] = useState(false);
  return <div className="offline-disclosure">
    <button onClick={() => setIsOpen((open) => !open)}>{title}<span>{isOpen ? '⌃' : '›'}</span></button>
    {isOpen && <div className="offline-disclosure-content">{children}</div>}
  </div>;
};

export const Stepper: React.FC<{ value: number; label: string; onChange: (val: number) => void; min?: number; max?: number }> = ({ value, label, onChange, min = 1, max = 365 }) => (
  <div className="offline-row offline-stepper-row"><span>{label}</span><div className="offline-stepper"><button onClick={() => onChange(Math.max(min, value - 1))}>−</button><button onClick={() => onChange(Math.min(max, value + 1))}>+</button></div></div>
);

export const SwipeableRow: React.FC<{ children: React.ReactNode; onEdit: () => void; onDelete: () => void }> = ({ children, onEdit, onDelete }) => (
  <div className="offline-row offline-saved-row"><div>{children}</div><div><button onClick={onEdit}>Editar</button><button onClick={onDelete}>Eliminar</button></div></div>
);
