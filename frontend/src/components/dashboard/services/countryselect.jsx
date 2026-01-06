import Select from "react-select"
import countryList from "react-select-country-list"
import { useMemo } from "react"

export default function CountrySelect({ form, update, hideLabel = false }) {
  const options = useMemo(() => countryList().getData(), [])

  // [수정] react-select 커스텀 스타일 정의
  const customStyles = {
    // 1. 입력창 (Control) 스타일
    control: (provided) => ({
      ...provided,
      minHeight: '42px', // 높이를 다른 input과 맞춤
      height: '42px',
      backgroundColor: 'var(--trade-card-bg, #1e222d)', // 배경색
      borderColor: 'var(--trade-border, #2a2e39)',      // 테두리 색상
      boxShadow: 'none',
      color: 'var(--trade-text, #d1d4dc)',              // 기본 텍스트 색상
      '&:hover': {
        borderColor: '#2962ff' // 호버 시 테두리 강조
      }
    }),
    
    // 2. 선택된 값 (Selected Value) 텍스트 색상
    singleValue: (provided) => ({
      ...provided,
      color: 'var(--trade-text, #d1d4dc)', 
    }),

    // 3. 입력 중인 텍스트 (Input) 색상
    input: (provided) => ({
      ...provided,
      color: 'var(--trade-text, #d1d4dc)', 
    }),

    // 4. 플레이스홀더 색상 (약간 흐리게)
    placeholder: (provided) => ({
      ...provided,
      color: 'var(--trade-subtext, #888)',
    }),

    // 5. 드롭다운 메뉴 (Menu) 배경
    menu: (provided) => ({
      ...provided,
      backgroundColor: 'var(--trade-card-bg, #1e222d)',
      border: '1px solid var(--trade-border, #2a2e39)',
      zIndex: 9999, // 모달 위로 올라오도록
    }),

    // 6. 드롭다운 항목 (Option) 스타일
    option: (provided, state) => ({
      ...provided,
      backgroundColor: state.isFocused ? 'var(--trade-hover, #2a2e39)' : 'transparent', // 포커스(호버) 배경
      color: 'var(--trade-text, #d1d4dc)', // 텍스트 색상
      cursor: 'pointer',
      '&:active': {
        backgroundColor: '#2962ff'
      }
    }),
  };

  return (
    <div className={hideLabel ? "" : "form-group"}>
      {!hideLabel && <label style={{ fontWeight: 'normal' }}>나라 선택</label>}
      <Select
        options={options}
        value={options.find((c) => c.value === form.country) || null}
        onChange={(e) => update("country", e.value)}
        placeholder="나라를 선택해주세요"
        isSearchable
        styles={customStyles} // [적용] 커스텀 스타일 적용
      />
    </div>
  )
}