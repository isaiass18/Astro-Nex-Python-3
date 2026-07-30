import React from 'react';

export interface ChartContext {
  cx: number;
  cy: number;
  radius: number;
  offsetDegree: number;
}

interface ChartSvgProps {
  width?: number;
  height?: number;
  svgContent?: string;
  children?: React.ReactNode;
}

export const ChartSvg: React.FC<ChartSvgProps> = ({
  width = 1000,
  height = 1000,
  svgContent,
  children
}) => {
  if (svgContent) {
    return (
      <svg 
        viewBox="0 0 1000 1000"
        width="100%" 
        height="100%" 
        style={{
          display: 'block',
          margin: '0 auto',
          backgroundColor: '#fff',
          borderRadius: '50%'
        }}
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
    );
  }

  return (
    <svg 
      viewBox={`0 0 ${width} ${height}`} 
      width="100%" 
      height="100%" 
      style={{
        display: 'block',
        margin: '0 auto',
        backgroundColor: '#fff',
        borderRadius: '50%'
      }}
    >
      <rect x="0" y="0" width={width} height={height} fill="#ffffff" rx="16" ry="16" />
      {children}
    </svg>
  );
};
