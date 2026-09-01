import "./ErrorNotice.css";

type ErrorNoticeProps = {
  className: string;
  message: string;
  title: string;
};

export function ErrorNotice({ className, message, title }: ErrorNoticeProps) {
  return (
    <div className={`${className} error-notice`} role="alert">
      <strong>{title}</strong>
      <span>{message}</span>
    </div>
  );
}
