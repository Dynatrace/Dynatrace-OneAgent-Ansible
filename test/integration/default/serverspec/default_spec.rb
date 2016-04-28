require 'serverspec'

# Required by serverspec
set :backend, :exec

describe file('/opt/ruxit') do
  it { should be_directory }
end
