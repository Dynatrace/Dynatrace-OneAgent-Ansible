# How to deploy Dynatrace OneAgent using Ansible (using an Ansible Dynamic Inventory)

These instructions assume that you have basic knowledge of Ansible, a simple yet extremely powerful IT automation tool that has been making our lives at Dynatrace easier since its earliest days. In this example, you’ll use Ansible to automatically roll out Dynatrace OneAgent to the nodes of an OpenShift cluster.

## 1. Create your Dynatrace account

If you are new to Dynatrace, sign up for your free trial at [http://www.dynatrace.com](http://www.dynatrace.com) and take the installer script url:

1. Select **Deploy Dynatrace** from the navigation menu.
2. Click the **Start installation** button.
3.  For **Linux**
   - Locate your `oneagent_installer_script_url`, as shown below.
   ![Alt text](https://user-images.githubusercontent.com/23307837/31117056-a912fb0c-a828-11e7-8020-f065adf65fa9.png)
4. For **Windows**
    - Rightclick on "Download agent.exe" button and select "Copy link address"

## 2. Obtain our Ansible role for Dynatrace OneAgent

The following command installs OneAgent with the role Dynatrace.OneAgent into the roles subdirectory within your current working directory:

```
ansible-galaxy install Dynatrace.OneAgent -p roles
```

## 2. Describe your cluster nodes via an Ansible inventory

Create a file called `hosts` inside your working directory and add a newline-separated list of cluster nodes, like this:

```
192.168.0.100
192.168.0.101
192.168.0.102
192.168.0.103
```

# 3. Define OneAgent deployment in an Ansible Playbook

With your cluster nodes identified, the only thing left to do is describe the deployment of OneAgent within the Ansible playbook in `playbook.yml`:

```
---
- hosts: all
  roles:
  - role: Dynatrace.OneAgent
    oneagent_installer_script_url: YOUR_ONEAGENT_INSTALLER_SCRIPT_URL
```

# 4. Run OneAgent deployment via Ansible

```
ansible-playbook --private-key=PRIVATE_KEY_FILE --user=REMOTE_USER playbook.yml 
```

- The `--private-key` option points Ansible to the private key file you created when provisioning your cluster in AWS.
- The `--user` option tells Ansible which user to use when connecting remotely to your cluster nodes. In case of OpenShift Origin, you would set this to `centos`.

# 5. Start your OpenShift applications

Once Ruxit Agent has been deployed to your cluster you simply start your OpenShift application as you normally would — Dynatrace will take care of the monitoring:

```
oc new-app .
```

Don’t forget that existing OpenShift applications must be restarted (for example, by temporarily reducing the number of pods for those applications to 0).
