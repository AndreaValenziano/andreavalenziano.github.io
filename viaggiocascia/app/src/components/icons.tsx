import type { SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement>

function Icon({ children, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.9}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  )
}

export const CalendarIcon = (p: IconProps) => (
  <Icon {...p}>
    <rect x="3" y="5" width="18" height="16" rx="2.5" />
    <path d="M3 10h18M8 3v4M16 3v4" />
  </Icon>
)

export const InfoIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 11v5M12 7.5v.5" />
  </Icon>
)

export const CheckSquareIcon = (p: IconProps) => (
  <Icon {...p}>
    <rect x="3.5" y="3.5" width="17" height="17" rx="3" />
    <path d="m8 12.5 2.8 2.8L16.5 9" />
  </Icon>
)

export const NotebookIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M6 3.5h12a1.5 1.5 0 0 1 1.5 1.5v14a1.5 1.5 0 0 1-1.5 1.5H6a1.5 1.5 0 0 1-1.5-1.5V5A1.5 1.5 0 0 1 6 3.5Z" />
    <path d="M8.5 3.5v17M12.5 8h4M12.5 12h4" />
  </Icon>
)

export const GearIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="3.2" />
    <path d="M12 2.8v2.4M12 18.8v2.4M21.2 12h-2.4M5.2 12H2.8M18.5 5.5l-1.7 1.7M7.2 16.8l-1.7 1.7M18.5 18.5l-1.7-1.7M7.2 7.2 5.5 5.5" />
  </Icon>
)

export const PhoneIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M5.5 4h3l1.7 4.2-2 1.6a12.5 12.5 0 0 0 6 6l1.6-2L20 15.5v3a1.5 1.5 0 0 1-1.6 1.5C10.6 19.6 4.4 13.4 4 5.6A1.5 1.5 0 0 1 5.5 4Z" />
  </Icon>
)

export const NavigationIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M20 4 4.5 10.5l6.5 2.5 2.5 6.5L20 4Z" />
  </Icon>
)

export const PlusIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 5v14M5 12h14" />
  </Icon>
)

export const TrashIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4.5 6.5h15M9.5 6.5V4.8A1.3 1.3 0 0 1 10.8 3.5h2.4a1.3 1.3 0 0 1 1.3 1.3v1.7M6.5 6.5l.8 12.2a1.5 1.5 0 0 0 1.5 1.3h6.4a1.5 1.5 0 0 0 1.5-1.3l.8-12.2" />
  </Icon>
)

export const PencilIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="m14.5 5.5 4 4L8 20l-4.5.5L4 16 14.5 5.5ZM12.5 7.5l4 4" />
  </Icon>
)

export const DownloadIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 4v11m0 0 4-4m-4 4-4-4M4.5 19.5h15" />
  </Icon>
)

export const UploadIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 15V4m0 0 4 4m-4-4-4 4M4.5 19.5h15" />
  </Icon>
)

export const StarIcon = (p: IconProps) => (
  <Icon {...p} fill="currentColor" stroke="none">
    <path d="m12 3 2.5 5.4 5.9.7-4.4 4 1.2 5.9L12 16l-5.2 3 1.2-5.9-4.4-4 5.9-.7L12 3Z" />
  </Icon>
)

export const ChevronDownIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="m6 9.5 6 6 6-6" />
  </Icon>
)
