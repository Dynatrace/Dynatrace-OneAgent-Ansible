require 'serverspec'

# Required by serverspec
set :backend, :exec

describe file('/opt/dynatrace') do
  it { should be_directory }
end
