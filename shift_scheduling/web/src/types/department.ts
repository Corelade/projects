export interface Department {
  id: number
  // name: string
  name: string
  min_staff: number
  max_staff: number
  deleted?: boolean
}

export type DepartmentInput = Omit<Department, 'id'>
