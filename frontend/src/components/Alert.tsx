import { ReactNode } from 'react';

type AlertProps = {
  children: ReactNode;
  variant?: 'default' | 'destructive';
};

type AlertDescriptionProps = {
  children: ReactNode;
};

export function Alert({ children, variant = 'default' }: AlertProps) {
  return <div className={`alert alert--${variant}`}>{children}</div>;
}

export function AlertDescription({ children }: AlertDescriptionProps) {
  return <div className="alert__description">{children}</div>;
}
