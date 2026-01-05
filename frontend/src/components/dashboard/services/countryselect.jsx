import Select from "react-select"
import countryList from "react-select-country-list"
import { useMemo } from "react"

export default function CountrySelect({ form, update, hideLabel = false }) {
  const options = useMemo(() => countryList().getData(), [])

  return (
    // hideLabel이 true일 경우 form-group 클래스(마진 등) 제거
    <div className={hideLabel ? "" : "form-group"}>
      {!hideLabel && <label style={{ fontWeight: 'normal' }}>나라 선택</label>}
      <Select
        options={options}
        value={options.find((c) => c.value === form.country) || null}
        onChange={(e) => update("country", e.value)}
        placeholder="Select country"
        isSearchable
        styles={{
            // "보안 설정" 스타일 내부에서 이질감 없도록 높이/보더 조정 (선택사항)
            control: (provided) => ({
                ...provided,
                minHeight: '38px',
                height: '38px',
            }),
        }}
      />
    </div>
  )
}