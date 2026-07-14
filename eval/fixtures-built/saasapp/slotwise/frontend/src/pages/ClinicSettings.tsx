export default function ClinicSettings({settings, onChange}) {
  return (
    <label>
      Automatically send appointment reminders
      <input
        type="checkbox"
        checked={!!settings.auto_send_reminders}
        onChange={(e) => onChange("auto_send_reminders", e.target.checked)}
      />
    </label>
  );
}
